# enrich SAML SP metadata with additional information using XSLT transformation

import requests
from xml.etree import ElementTree as etree

METADATA_URL = 'https://login.kramerius.mzk.cz/realms/kramerius/broker/federation/eduid/endpoint/descriptor'
METADATA_ORGANIZATION_URL = 'https://www.mzk.cz/'
METADATA_DISPLAYNAME_CS = 'Kramerius 7'
METADATA_DESCRIPTION_CS = 'Kramerius 7 digitální knihovna'
METADATA_INFORMATION_URL_CS = 'https://www.digitalniknihovna.cz/mzk/about'
METADATA_PRIVACY_STATEMENT_URL_CS = 'https://www.mzk.cz/osobniudajeinfo'
METADATA_ORGANIZATION_NAME_CS = 'Moravská zemská knihovna'
METADATA_DISPLAYNAME_EN = 'Kramerius 7'
METADATA_DESCRIPTION_EN = 'Kramerius 7 digital library'
METADATA_INFORMATION_URL_EN = 'https://www.digitalniknihovna.cz/mzk/about'
METADATA_PRIVACY_STATEMENT_URL_EN = 'https://www.mzk.cz/en/personaldatainfo'
METADATA_ORGANIZATION_NAME_EN = 'Moravian Library'
METADATA_TECHNICAL_PEOPLE = [
        dict(first='Thanh Quang', last='Tran', mail='quangthanh.tran@mzk.cz'),
        dict(first='Petr', last='Žabička', mail='zabicka@mzk.cz'),
]

import io


def get_metadata():
    r = requests.get(METADATA_URL)
    xml_document = etree.fromstring(r.text)

    namespaces = dict(
        [node for _, node in
         etree.iterparse(io.StringIO(r.text), events=['start-ns'])]
    )

    return dict(
        document=xml_document,
        namespaces=namespaces
    )


def indent(elem, level=0):
    """ stolen from https://stackoverflow.com/a/4590052/7554925 """
    i = "\n" + level * "  "
    j = "\n" + (level - 1) * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


if __name__ == '__main__':
    metadata = get_metadata()

    document = metadata['document']
    namespaces = metadata['namespaces']
    md_ns = namespaces['md']
    ui_ns = 'urn:oasis:names:tc:SAML:metadata:ui'
    attr_ns = 'urn:oasis:names:tc:SAML:metadata:attribute'
    refeds_ns = 'http://refeds.org/metadata'
    namespaces['mdui'] = ui_ns
    for ns in namespaces:
        etree.register_namespace(ns, namespaces[ns])
    #
    descriptor = document.find('md:SPSSODescriptor', namespaces=namespaces)
    print(descriptor)
    # add Extensions element
    extensions = etree.Element(f'{{{md_ns}}}Extensions')
    descriptor.insert(0, extensions)
    # add EntityAttributes element
    entity_attributes = etree.SubElement(extensions, 'EntityAttributes')
    entity_attributes.set('xmlns', attr_ns)
    attribute = etree.SubElement(entity_attributes, 'Attribute')
    attribute.set('xmlns', 'urn:oasis:names:tc:SAML:2.0:assertion')
    attribute.set('Name', 'http://macedir.org/entity-category')
    attribute.set('NameFormat', 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri')
    attr_value = etree.SubElement(attribute, 'AttributeValue')
    attr_value.text = 'http://www.geant.net/uri/dataprotection-code-of-conduct/v1'
    # add UIInfo element
    ui_info = etree.SubElement(extensions, f'{{{ui_ns}}}UIInfo')
    # add en DisplayName element
    display_name = etree.SubElement(ui_info, f'{{{ui_ns}}}DisplayName')
    display_name.set('xml:lang', 'en')
    display_name.text = METADATA_DISPLAYNAME_EN
    # add en Description element
    description = etree.SubElement(ui_info, f'{{{ui_ns}}}Description')
    description.set('xml:lang', 'en')
    description.text = METADATA_DESCRIPTION_EN
    # add en InformationURL element
    information_url = etree.SubElement(ui_info, f'{{{ui_ns}}}InformationURL')
    information_url.set('xml:lang', 'en')
    information_url.text = METADATA_INFORMATION_URL_EN
    # add en Privacy statement element
    information_url = etree.SubElement(ui_info, f'{{{ui_ns}}}PrivacyStatementURL')
    information_url.set('xml:lang', 'en')
    information_url.text = METADATA_PRIVACY_STATEMENT_URL_EN

    # add cs DisplayName element
    display_name = etree.SubElement(ui_info, f'{{{ui_ns}}}DisplayName')
    display_name.set('xml:lang', 'cs')
    display_name.text = METADATA_DISPLAYNAME_CS
    # add cs Description element
    description = etree.SubElement(ui_info, f'{{{ui_ns}}}Description')
    description.set('xml:lang', 'cs')
    description.text = METADATA_DESCRIPTION_CS
    # add cs InformationURL element
    information_url = etree.SubElement(ui_info, f'{{{ui_ns}}}InformationURL')
    information_url.set('xml:lang', 'cs')
    information_url.text = METADATA_INFORMATION_URL_CS
    # add cs Privacy statement element
    information_url = etree.SubElement(ui_info, f'{{{ui_ns}}}PrivacyStatementURL')
    information_url.set('xml:lang', 'cs')
    information_url.text = METADATA_PRIVACY_STATEMENT_URL_CS

    # add Organization element
    organization = etree.SubElement(document, f'{{{md_ns}}}Organization')
    organization_data = {
        'en': dict(
            name=METADATA_ORGANIZATION_NAME_EN,
            display_name=METADATA_ORGANIZATION_NAME_EN, url=METADATA_ORGANIZATION_URL
        ),
        'cs': dict(
            name=METADATA_ORGANIZATION_NAME_CS,
            display_name=METADATA_ORGANIZATION_NAME_CS, url=METADATA_ORGANIZATION_URL
        )
    }

    for lang, org in organization_data.items():
        org_name = etree.SubElement(organization,
                                    f'{{{md_ns}}}OrganizationName')
        org_name.set('xml:lang', lang)
        org_name.text = org['name']

    for lang, org in organization_data.items():
        org_display_name = etree.SubElement(organization,
                                            f'{{{md_ns}}}OrganizationDisplayName')
        org_display_name.set('xml:lang', lang)
        org_display_name.text = org['display_name']

    for lang, org in organization_data.items():
        org_url = etree.SubElement(organization, f'{{{md_ns}}}OrganizationURL')
        org_url.set('xml:lang', lang)
        org_url.text = org['url']

    for person in METADATA_TECHNICAL_PEOPLE:
        # add ContactPerson element
        contact = etree.Element(f'{{{md_ns}}}ContactPerson')
        document.append(contact)
        contact.set('contactType', 'technical')
        # add contact people
        etree.SubElement(contact, f'{{{md_ns}}}GivenName').text = person['first']
        etree.SubElement(contact, f'{{{md_ns}}}SurName').text = person['last']
        etree.SubElement(contact, f'{{{md_ns}}}EmailAddress').text = 'mailto:' + \
                                                                 person[
                                                                     'mail']

    # indent metadata
    indent(document)

    result = etree.tostring(document, encoding='utf-8')

    open('metadata.xml', 'wb').write(result)
