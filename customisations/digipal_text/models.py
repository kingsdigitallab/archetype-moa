from django.db import models
from mezzanine.conf import settings
from django.contrib.contenttypes.models import ContentType
from digipal_text.models import TextContentXML, TextUnits, TextUnit, ClassProperty
from django.db.models import Q
import os
import re
import logging
import digipal.models
import json
from digipal.utils import urlencode
dplog = logging.getLogger('digipal_debugger')

from digipal import models as digipal_models

ItemPart = digipal_models.ItemPart

if 1:
    OTHER_CLERICAL = u'Other Ecclesiastical'

    hnumber_to_issuer_types = {
        '0': '0/X/Y',
        '1': 'Royal',
        '2': 'Ecclesiastical',
        '3': 'Private',
        '4': 'Settlement or agreement',
        '5': '5/X/Y',
        '6': '6/X/Y',
    }

    def itempart_get_poms_people(self):
        '''Load and cache all the records from the poms table
            related to this itempart'''
        attr_name = '_pom_people'
        ret = getattr(self, attr_name, None)
        if ret is None:
            ret = []
            if self.historical_item:
                from digipal import utils
                catnum = self.get_hnumber()
                if catnum:
                    query = 'select * from poms_charter_info where helperhnumber = %s '
                    ret = utils.sql_select_dict(query, [catnum])

            setattr(self, attr_name, ret)

        return ret

    def itempart_get_medieval_archive(self):
        return self.get_beneficiaries(institution_only=True)

    def itempart_get_beneficiaries(self, institution_only=False):
        people = self.get_poms_people()
        # ret = [re.sub(ur'\(fd[^)]+\)', '', person['persondisplayname'])
        ret = [re.sub(ur'\([^)]*\d[^)]*\)', '', person['persondisplayname'])
               for person in people
               if person['isissuer'] == '0'
               and (not institution_only or person['genderkeyid'] == '5')
               ]
        return ret or None

    def itempart_get_issuers(self):
        people = self.get_poms_people()
        ret = [person['persondisplayname']
               for person in people if person['isissuer'] == '1']
        return ret or None

    def itempart_get_hnumber(self):
        '''E.g. 1/7/170 '''
        ret = None
        if self.historical_item:
            catnum = self.historical_item.catalogue_numbers.filter(
                source__id=2).first()
            if catnum:
                ret = catnum.number
                ret = re.sub('(?usi)\s*Document\s*', '', ret)
        return ret

    def itempart_get_issuer_types(self):
        return itempart_get_issuer_types_from_hnumber(self)
        # return itempart_get_issuer_types_from_issuers(self)

    def itempart_get_issuer_types_from_hnumber(self):
        ret = None
        hnumber = self.get_hnumber()
        if hnumber:
            ret = hnumber_to_issuer_types.get(hnumber[0], None)
            if ret and hnumber[0] == '2':
                # Ecclesiastical,. let's add more specific type(s) as well
                # based on the issuer name this time
                specifics = itempart_get_issuer_types_from_issuers(self)
                if specifics:
                    ret = [ret]
                    ecclesiasticals = ['Papal', 'Episcopal', OTHER_CLERICAL]
                    # we return ONLY one subcategory, either papal, Episcopal or other
                    # in case we have multiple types:
                    # papal take priority over epi. which takes prio. over
                    # other
                    for subcategory in ecclesiasticals:
                        if subcategory in specifics:
                            ret.append(subcategory)
                            # print subcategory, specifics
                            break
        return ret or 'Unspecified'

    def itempart_get_issuer_types_from_issuers(self):
        ret = []
        issuers = self.get_issuers()
        if issuers:
            for issuer in issuers:
                issuer_type = 'Private'
                if re.search(ur'\b(king|queen)\b', issuer.lower()):
                    issuer_type = u'Royal'
                if re.search(ur'\b(bishop)\b', issuer.lower()):
                    issuer_type = u'Episcopal'
                if re.search(ur'\b(pope)\b', issuer.lower()):
                    issuer_type = u'Papal'
                # TODO: check this list! (it's mine, created manually from a
                # list of issuers)
                if re.search(ur'\b(abbey|abbot|almoner|canon|chaplain|chapter|clergy|archdeacon|deacon|dean|prior|priory|rector|vicar)\b', issuer.lower()):
                    issuer_type = OTHER_CLERICAL
                if issuer_type:
                    ret.append(issuer_type)
            ret = list(set(ret))
        return ret or None

    ItemPart.get_poms_people = itempart_get_poms_people
    ItemPart.get_medieval_archive = itempart_get_medieval_archive
    ItemPart.get_beneficiaries = itempart_get_beneficiaries
    ItemPart.get_issuers = itempart_get_issuers
    ItemPart.get_issuer_types = itempart_get_issuer_types
    ItemPart.get_hnumber = itempart_get_hnumber

# LEAVE THIS IMPORT EVEN IF IT IS NOT USED...
# We do this because of the customisations of ItemPart above
# Another module can import Image from this module to make sure
# the ItemPart customisations are applied
# The faceted search for image will fail while trying to import Image
# LEAVE THIS IMPORT EVEN IF IT IS NOT USED...
from digipal.models import Image
from digipal.models import Graph

# Customise TextContentXML
# To auto-mark-up on save()
if not(getattr(TextContentXML, 'is_customised', False)):
    TextContentXML.is_customised = True

    TextContentXML_save_base = TextContentXML.save

    def TextContentXML_save(self, *args, **kwargs):
        if self.text_content and self.text_content.type and self.text_content.type.slug == 'transcription':
            self.convert()
        TextContentXML_save_base(self, *args, **kwargs)
    TextContentXML.save = TextContentXML_save

    TextContentXML_convert_base = TextContentXML.convert

    def TextContentXML_convert(self):
        '''
        This method MUST remain idempotent, that is, converting a second or more
        times produces doesn't change the result from the previous conversion.

        It is called by the auto-convert button on the Text Editor to
        clean and mark-up editorial conventions. E.g. | => <br/>

        For specific projects, inherit this class and override this method. 
        Keep generic conversion here.
        '''
        content = self.content

        if content:

            # remove empty spans
            content = re.sub(ur'<span[^>]*></span>', u'', content)

            # convert () into expansions
            content = re.sub(
                ur'\(([^)<>]{1,50})\)', ur'<span data-dpt="ex" data-dpt-cat="chars">\1</span>', content)

            # convert <> into supplied
            content = re.sub(
                ur'&lt;(.*?)&gt;', ur'<span data-dpt="supplied" data-dpt-cat="chars">\1</span>', content)

            # convert 7 into tironian sign
            content = re.sub(ur'\b7\b', u'\u204a', content)

            convert_pipes = 1
            if convert_pipes:
                # remove all line break markup so it can be reconstructed from
                # pipes
                while True:
                    l = len(content)
                    content = re.sub(
                        ur'<span data-dpt="lb"[^>]*>([^<]*)</span>', ur'\1', content)
                    if len(content) == l:
                        break

                # convert WORD|WORD into WORD-|WORD
                content = re.sub(ur'(?musi)(\w)\|(\w)', ur'\1-|\2', content)
                # convert - | into -|
                content = re.sub(ur'(?musi)-s+\|', ur'-|', content)

                # convert | and -| into spans
                #content = re.sub(ur'(-?\|+)', ur'<span data-dpt="lb" data-dpt-cat="sep">\1</span>', content)
                content = re.sub(
                    ur'(-?\|+)', ur'<span data-dpt="lb" data-dpt-src="ms">\1</span>', content)

            # remove nested line break spans (due to bugs with multiple
            # conversions)
            if 1:
                while True:
                    l = len(content)
                    content = re.sub(ur'(<span[^>]*>)\1([^<>]*)(</span>)\3',
                                     ur'\1\2\3', content)
                    if len(content) == l:
                        break

            #content = re.sub(ur'(<br\s*/?>\s*)+', u'<br/>', content)
            self.content = content

        TextContentXML_convert_base(self)
    TextContentXML.convert = TextContentXML_convert


class Clauses(TextUnits):
    '''Virtual Model Class that represents a unit of text in a TextContentXML'''

    def findall_xml_elements(self, root):
        return root.findall("//span[@data-dpt='clause']")

    def new_unit(self):
        return Clause()

    def load_records_iter(self):
        # actually find and load the requested records
        aids = self.get_bulk_ids()

        debug = 0

        # get all the texts
        # TODO: move that 'pre' block to the parent class
        records = TextContentXML.objects.all()
        if 0:
            records = records.filter(text_content__type__slug='transcription')
        if self.options['select_related']:
            records = records.select_related(*self.options['select_related'])
        if self.options['prefetch_related']:
            records = records.prefetch_related(
                *self.options['prefetch_related'])

        # TODO: optimise for in_bulk()
        for content_xml in records.iterator():
            if debug:
                print 'IP #%s, TC #%s, TCX #%s: %s' % (content_xml.text_content.item_part.id, content_xml.text_content.id, content_xml.id, content_xml.text_content)
            if not content_xml.content:
                continue

            # get all the entries in this content
            from digipal.utils import get_xml_from_unicode, get_unicode_from_xml

            idcount = {}

            # print repr(content_xml.content)

            root = get_xml_from_unicode(
                content_xml.content, True, add_root=True)

            pos = 0
            # TODO: optimise for in_bulk()
            for clause_xml in self.findall_xml_elements(root):
                pos += 1

                # get the text only for that element
                clause_obj = self.new_unit()

                from digipal_text.views import viewer
                elementid = viewer.get_elementid_from_xml_element(
                    clause_xml, idcount
                )
                if elementid:
                    clause_obj.elementid = json.dumps(elementid)
                    clause_obj.unitid = viewer.get_unitid_from_xml_elementid(
                        elementid
                    )
                    clause_obj.content_xml = content_xml
                    clause_obj.content = get_unicode_from_xml(
                        clause_xml, text_only=False)

                    clause_obj.set_from_xml_element(clause_xml)

                    yield clause_obj


class Clause(TextUnit):
    @ClassProperty
    @classmethod
    def objects(cls, *args, **kwargs):
        return Clauses()

    def set_from_xml_element(self, element):
        self.clause_type = element.get('data-dpt-type', 'unspecified')

    def get_elementid(self):
        return self.elementid

    def get_absolute_url(self):
        metas = {'subl': [self.get_elementid()]}
        return super(Clause, self).get_absolute_url(location_type='default', metas=metas)

    def get_label(self):
        return '%s (%s)' % (self.clause_type, self.__class__.__name__)

# People clause

class People(Clauses):
    def findall_xml_elements(self, root):
        return root.findall("//span[@data-dpt='person']")

    def new_unit(self):
        return Person()


class Person(Clause):
    @ClassProperty
    @classmethod
    def objects(cls, *args, **kwargs):
        return People()

    def set_from_xml_element(self, element):
        super(Person, self).set_from_xml_element(element)

        person_type = element.attrib.get('data-dpt-type', None)
        self.clause_type = 'Person Name'

        # match instance of a title to predefined categories
        # e.g. Vic -> Vicecomes
        if person_type == 'title':
            types = [
                'Iusticia', 'Vicecomes', 'Cancellarius', 'Camerarius',
                'Constabularius', 'Marescallus', 'Clericus', 'Ballivus',
                'Serviens'
            ]
            import difflib
            from digipal import utils as dputils
            content_str = dputils.get_unicode_from_xml(element, text_only=True)
            best_matches = difflib.get_close_matches(
                content_str, types, cutoff=0.2)
            self.clause_type = best_matches[0] if best_matches else content_str


# Place clause

class Places(Clauses):
    def findall_xml_elements(self, root):
        return root.findall("//span[@data-dpt='place']")

    def new_unit(self):
        return Place()


class Place(Clause):
    @ClassProperty
    @classmethod
    def objects(cls, *args, **kwargs):
        return Places()

    def set_from_xml_element(self, element):
        super(Place, self).set_from_xml_element(element)

        place_type = element.attrib.get('data-dpt-type', None)
        self.clause_type = 'Place Name'


from digipal.models import set_additional_models_methods
set_additional_models_methods()
