# Customise the faceted search settings
import re
from digipal.views.faceted_search.settings import FACETED_SEARCH, remove_fields_from_faceted_search, get_content_type_from_key, FacettedType

# Hide locus and hi_format columns (see first Site testing for MoA)
# Unused in MoA
remove_fields_from_faceted_search(['hi_format'])
# Unused in MoA MS (single sheets)
remove_fields_from_faceted_search(['locus'], 'manuscripts')
remove_fields_from_faceted_search(['locus'], 'graphs')
# Make Locus a facet of Image, that way we can easily display faces by default
images = FacettedType.fromKey('images')
locus = images.getField('locus')
locus['count'] = True
images.addFieldToOption(key=locus['key'], after_key='mp_permission')

# for ftype in FACETED_SEARCH['types']:
#     ftype['private'] = (ftype['key'] not in ['manuscripts', 'images'])
# FACETED_SEARCH['type_keys']['manuscripts']


# Remove scribes as requested in project meeting
FACETED_SEARCH['type_keys']['scribes']['disabled'] = True

''' TODO
    add repo city, repo place, shelfmark, cat num, md date, doc type, link to record
    highlight keywords
    content on second line
    snippet or full clause
'''
from copy import deepcopy
clauses = deepcopy(FACETED_SEARCH['type_keys']['textunits'])
clauses.update({
    'disabled': False,
    'key': 'clauses',
    'label': 'Clause',
    'model': 'mofa.customisations.digipal_text.models.Clause',
    'views': [
        {'icon': 'list', 'label': 'List View',
            'key': 'list', 'params': {'hide_image_cols': 1}},
        {'icon': 'th-list', 'label': 'List + Images View',
            'key': 'images', 'template': 'list'},
    ],
})
FACETED_SEARCH['types'].append(clauses)

clauses = deepcopy(clauses)
clauses.update({
    'disabled': False,
    'key': 'people',
    'label': 'Person',
    'label_plural': 'People',
    'model': 'mofa.customisations.digipal_text.models.Person',
})
FACETED_SEARCH['types'].append(clauses)

for field in clauses['fields']:
    if field['key'] == 'clause_type':
        field['label'] = 'Category'

{'key': 'clause_type', 'label': 'Clause Type', 'path': 'clause_type',
    'search': True, 'viewable': True, 'type': 'code', 'count': True},

#clauses['fields'].append({'key': 'issuer', 'label': 'Issuer', 'path': 'issuer', 'search': True, 'viewable': True, 'type': 'text', 'line': 0})


def add_issuers_to_content_type(content_type_key, relative_path_to_item_part='', model_import_path='', nocols=False):
    # if nocols = True => fields not added to the table columns
    content_type = get_content_type_from_key(content_type_key)
    if model_import_path:
        content_type['model'] = model_import_path

    #fields_lists = ['column_order', 'filter_order', 'sorted_fields']
    fields_lists = ['filter_order']
    if not nocols:
        fields_lists.append('column_order')

    content_type['filter_order'] = FacettedType.fromKey(
        content_type_key).getFilterKeys()
    content_type['column_order'] = content_type.get('column_order', [
                                                    f['key'] for f in content_type['fields'] if f.get('viewable', False)])

    content_type['fields'].append({
        'key': 'issuer_type',
        'label': 'Issuer Type',
        'path': '%sget_issuer_types' % relative_path_to_item_part,
        'search': False, 'viewable': True,
        'type': 'title', 'line': 0, 'count': True,
        'multivalued': True
    })
    content_type['fields'].append({
        'key': 'issuer', 'label': 'Issuer',
        'path': '%sget_issuers' % relative_path_to_item_part,
        'search': not nocols, 'viewable': True,
        'type': 'title', 'line': 0, 'count': True,
        'multivalued': True
    })
    if 0:
        content_type['fields'].append({
            'key': 'medieval_archive', 'label': 'Institutional Beneficiary',
            'path': '%sget_medieval_archive' % relative_path_to_item_part,
            'search': not nocols, 'viewable': True,
            'type': 'title', 'line': 0, 'count': True,
            'multivalued': True
        })
    content_type['fields'].append({
        'key': 'beneficiary', 'label': 'Named Beneficiary',
        'path': '%sget_beneficiaries' % relative_path_to_item_part,
        'search': not nocols, 'viewable': True,
        'type': 'title', 'line': 0, 'count': True,
        'multivalued': True
    })

    if 'filter_order' in fields_lists:
        content_type['filter_order'].append('issuer_type')
    for meta_name in fields_lists:
        content_type[meta_name].append('issuer')
        # content_type[meta_name].append('medieval_archive')
        content_type[meta_name].append('beneficiary')


# hide hands from faceted saerch
get_content_type_from_key('hands')['disabled'] = True

# graphs > filters > 'hand_date' => 'hi_date'
gs = FacettedType.fromKey('graphs')
gs.options['filter_order'] = [
    ('hi_date' if col == 'hand_date' else col) for col in gs.options['filter_order']]

remove_fields_from_faceted_search(['hand_label', 'hand_date', 'hand_place'])

if 1:
    for ft in FacettedType.getAll():
        ft.setDateRange([1094, 1250])

        if 0:
            hi_date = ft.getField('hi_date')
            if hi_date:
                path = re.sub(ur'\.get_date_sort',
                              ur'.get_date_sort_range_diff', hi_date['path'])
                #hi_date_type = {'key': 'hi_date_type', 'label': 'Date precision', 'path': path, 'viewable': False, 'search': False, 'type': 'boolean', 'count': True, 'labels': {0: 'Not precise', 1: 'Precise'}}
                hi_date_type = {'key': 'hi_date_type', 'label': 'Date precision', 'path': path, 'viewable': False,
                                'search': False, 'type': 'boolean', 'count': True, 'labels': {0: 'Not precise', 1: 'Precise'}}
                ft.addField(hi_date_type, 'hi_date')
                ft.addFieldToOption('filter_order', 'hi_date_type', 'hi_date')
            else:
                pass

# add C,F and CF to graphs
empty_mappings = FacettedType.getFragment('field_mapping_empty')
gs.options['fields'].append({'key': 'component', 'label': 'Component', 'path': 'graph_components.all.component.name',
                             'type': 'id', 'filter': True, 'count': True, 'multivalued': True, 'mapping': empty_mappings})
gs.options['fields'].append({'key': 'feature', 'label': 'Feature', 'path': 'graph_components.all.features.all.name',
                             'type': 'id', 'filter': True, 'count': True, 'multivalued': True, 'mapping': empty_mappings})
gs.options['fields'].append({'key': 'cf', 'label': 'Component-Feature', 'path': 'get_component_feature_labels',
                             'type': 'id', 'filter': True, 'count': True, 'multivalued': True, 'mapping': empty_mappings})

# add Position
gs.options['fields'].append({'key': 'position', 'label': 'Position', 'path': 'get_aspect_positions',
                             'type': 'id', 'filter': True, 'count': True, 'multivalued': True})

gs.addFieldsToOption(
    'filter_order', ['component', 'feature', 'cf', 'position'], 'allograph')


# issuers

add_issuers_to_content_type(
    'manuscripts', '', 'mofa.customisations.digipal_text.models.ItemPart')
add_issuers_to_content_type('clauses', 'content_xml.text_content.item_part.')
add_issuers_to_content_type('images', 'item_part.',
                            'mofa.customisations.digipal_text.models.Image')
add_issuers_to_content_type('texts', 'text_content.item_part.',
                            'mofa.customisations.digipal_text.models.TextContentXML')
add_issuers_to_content_type('graphs', 'annotation.image.item_part.',
                            'mofa.customisations.digipal_text.models.Graph', True)

# add C,F and CF to images
ims = FacettedType.fromKey('images')
ims.options['fields'].append({'key': 'component', 'label': 'Component', 'path': 'annotation_set.all.graph.graph_components.all.component.name',
                              'type': 'id', 'filter': True, 'count': True, 'multivalued': True, 'mapping': empty_mappings})
ims.options['fields'].append({'key': 'feature', 'label': 'Feature', 'path': 'annotation_set.all.graph.graph_components.all.features.all.name',
                              'type': 'id', 'filter': True, 'count': True, 'multivalued': True, 'mapping': empty_mappings})
ims.options['fields'].append({'key': 'cf', 'label': 'Component-Feature', 'path': 'annotation_set.all.graph.get_component_feature_labels',
                              'type': 'id', 'filter': True, 'count': True, 'multivalued': True, 'mapping': empty_mappings})

# add new fields to filter list
ims.addFieldsToOption(
    'filter_order', ['component', 'feature', 'cf'])

# vis categories

FacettedType.getGlobal('visualisation').update({
    'categories': ['hi_type', 'clause_type', 'beneficiary', 'issuer', 'issuer_type'],
})

# add authenticity
for ft in FacettedType.getAll():
    if 0:
        shelfmark_field = ft.getField('shelfmark')
        if shelfmark_field:
            path_to_ip = shelfmark_field['path'].replace(
                'current_item.shelfmark', '')
            definition = {'key': 'authenticity', 'label': 'Contemporaneity', 'path': '%sget_authenticity_labels' % path_to_ip,
                          'type': 'id', 'filter': True, 'count': True, 'multivalued': True}
            ft.addField(definition)
            ft.addFieldToOption('filter_order', definition['key'])
            shelfmark_field['path_result'] = '%sget_shelfmark_with_auth' % path_to_ip

# special for MoA, show the Text Date instead of the HI date
for ft in FacettedType.getAll():
    for field in ft.getFields():
        l = len(field['path'])
        field['path'] = re.sub(
            ur'\.get_date_sort', ur'.get_first_text.get_date_sort', field['path'])
        if len(field['path']) != l:
            field['label'] = 'Text Date'

gs.fields.append({'key': 'note', 'label': 'Note', 'path': 'annotation.display_note',
                  'search': True, 'viewable': True, 'type': 'xml'})
gs.options['column_order'].append('note')

# Made notes searchable
if 0:
    gd = FACETED_SEARCH['type_keys']['graphs']
    gd['fields'].append({'key': 'note', 'label': 'Note', 'path': 'annotation.display_note',
                         'search': True, 'viewable': True, 'type': 'xml'})
    gd['column_order'].append('note')

FACETED_SEARCH['type_keys'] = {}
for t in FACETED_SEARCH['types']:
    FACETED_SEARCH['type_keys'][t['key']] = t
