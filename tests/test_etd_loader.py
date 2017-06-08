from unittest import TestCase
import os
from etd_loader import IdStore, EtdLoader
import tempfile
import shutil
import logging
import xml.etree.ElementTree as ElementTree
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)


class EtdLoaderTest(TestCase):
    def setUp(self):
        self.base_path = tempfile.mkdtemp()
        self.loader = EtdLoader(self.base_path, 'host', 'username', 'password', '/path', 22, 'mail_host',
                                'mail_username', 'mail_password', 123, 'marc_mail_to')
        self.loader.now = datetime(2017, 4, 5)

    def tearDown(self):
        shutil.rmtree(self.base_path, ignore_errors=True)

    def test_extract_etd_id_from_filename(self):
        self.assertEqual('395013', EtdLoader._extract_etd_id_from_filename('etdadmin_upload_395013.zip'))

    # def test_create_marc_record(self):
    #     self.assertTrue(os.path.exists(self.loader.etd_to_be_marced_path))
    #     # shutil.copy('./tests/etdadmin_upload_9900.zip', self.loader.etd_to_be_marced_path)
    #     shutil.copy('/Users/justinlittman/Data/esp/sample_etds/etdadmin_upload_99010.zip', self.loader.etd_to_be_marced_path)
    #     # self.loader.create_marc_record('etdadmin_upload_9900.zip', 'http://foo.com/9900')
    #     self.loader.create_marc_record('etdadmin_upload_99010.zip', 'http://foo.com/99010')

    # TODO: test create MARC record missing metadata file
    def assert_field(self, field, subfield_map, indicator1=' ', indicator2=' '):
        self.assertEqual(indicator1, field.indicator1)
        self.assertEqual(indicator2, field.indicator2)
        for subfield_tag, subfield_value in subfield_map.items():
            self.assertEqual(subfield_value, field[subfield_tag])

    def test_create_empty_marc_record(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N" />
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assertEqual('00000nam  22000007a 4500', record.leader)
        self.assertEqual('MiAaPQ', record['003'].data)
        self.assertEqual('m    fo  d        ', record['006'].data)
        self.assertEqual('cr mnu   aacaa', record['007'].data)
        self.assert_field(record['040'], {'a': 'MiAaPQ', 'b': 'eng', 'c': 'DGW', 'd': 'DGW'})
        self.assert_field(record['049'], {'a': 'DGWW'})
        self.assert_field(record['504'], {'a': 'Includes bibliographical references.'})
        self.assert_field(record['538'], {'a': 'Mode of access: Internet'})
        self.assert_field(record['852'], {'b': 'gwg ed', 'h': 'GW: Electronic Dissertation'}, indicator1='8')
        self.assert_field(record['856'], {'u': 'http://repo/11053', 'z': 'Click here to access.'}, indicator1='4',
                          indicator2='0')
        self.assert_field(record['996'], {'a': 'New title added ; 20170405'})
        self.assert_field(record['998'], {'c': 'gwjshieh ; UMI-ETDxml conv ; 20170405'})

    def test_create_marc_record_516(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes" />
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['516'], {'a': 'Text (PDF: 97 p.)'})

    def test_create_marc_record_520(self):
        # TODO: Need example of HTML markup to test.
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_content>
                        <DISS_abstract>
                          <DISS_para>After the attacks on the World Trade Centers on September 11, 2001, engineers agreed that work needed to be done to increase the robustness of structures.  Research has increased in many areas including progressive collapse of structures, structural response to fires, and other effects of extreme loading conditions.  As a result of this research, building codes have been altered to include increased protection against these events.  One newly implemented structural integrity provision for the 2009 International Building Code (IBC) includes the need to provide a minimum tensile capacity in simple shear steel connections.</DISS_para>
                          <DISS_para>This thesis is a continuation of a previously started project by the Department of Civil and Environmental Engineering at George Washington University for the American Institute of Steel Construction.  The work included experimental testing of simple shear all-bolted single-angle connections to determine the failure mechanism and ultimate strength.  The single-angle connection is one of the most economical and widely used simple shear connections in buildings and therefore testing was undertaken to ensure that these connections would comply with the new structural integrity provisions.  The angles failed due to two mechanisms: bolt tensile failure and shear fracture of the angle.</DISS_para>
                          <DISS_para>Based on the results of the single-angle experiments, a finite-element model was created in order to investigate an interesting outcome regarding the prying action of the single-angle connection tests. The observed strength is about three times larger than the current AISC prying equations predict, which is overly conservative.  The AISC prying equations are largely based on research which involved relatively rigid symmetrical tee-sections so the behavior of relatively flexible single-angles would be expectantly different. </DISS_para>
                          <DISS_para>Prior to the single-angle tests, there is very minimal published research on single-angles under tensile load.  The test data supporting the AISC prying equations was mostly based on less flexible connections.  Prying action involves a complex interaction between tensile, shear, and moments that occurs more so when elements are flexible and able to have large deformations, effectively causing an increase in the load on the bolts.  </DISS_para>
                          <DISS_para>Following the finite-element model and a study of different methods for calculating the prying action capacity, it was determined that a new model should be adopted by AISC for prying action of single-angles because the current prying equations do not accurately predict the behavior for single-angle connections. The British Steel Construction Institute P212 publication presents a large displacement analysis method in its Appendix D for determining the effects of prying action on bolt strength for double angle connections.  In this thesis, that model has been altered for single-angles and reasonably predicts the capacity of the tested connection by determining a reduced bolt stress.  Therefore an equation for the limit state of bolt tensile failure with prying action for single-angles has been proposed to be adopted by AISC for connections with angle thickness of 5/8-in or less. Typically, simple-shear connections such as single-angles are relatively flexible and therefore more research should be conducted on flexible bolted connections where prying action would occur.</DISS_para>
                        </DISS_abstract>
                    </DISS_content>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['520'], {
            'a': 'After the attacks on the World Trade Centers on September 11, 2001, engineers agreed that work needed to be done to increase the robustness of structures.  Research has increased in many areas including progressive collapse of structures, structural response to fires, and other effects of extreme loading conditions.  As a result of this research, building codes have been altered to include increased protection against these events.  One newly implemented structural integrity provision for the 2009 International Building Code (IBC) includes the need to provide a minimum tensile capacity in simple shear steel connections.This thesis is a continuation of a previously started project by the Department of Civil and Environmental Engineering at George Washington University for the American Institute of Steel Construction.  The work included experimental testing of simple shear all-bolted single-angle connections to determine the failure mechanism and ultimate strength.  The single-angle connection is one of the most economical and widely used simple shear connections in buildings and therefore testing was undertaken to ensure that these connections would comply with the new structural integrity provisions.  The angles failed due to two mechanisms: bolt tensile failure and shear fracture of the angle.Based on the results of the single-angle experiments, a finite-element model was created in order to investigate an interesting outcome regarding the prying action of the single-angle connection tests. The observed strength is about three times larger than the current AISC prying equations predict, which is overly conservative.  The AISC prying equations are largely based on research which involved relatively rigid symmetrical tee-sections so the behavior of relatively flexible single-angles would be expectantly different. Prior to the single-angle tests, there is very minimal published research on single-angles under tensile load.  The test data supporting the AISC prying equations was mostly based on less flexible connections.  Prying action involves a complex interaction between tensile, shear, and moments that occurs more so when elements are flexible and able to have large deformations, effectively causing an increase in the load on the bolts.  Following the finite-element model and a study of different methods for calculating the prying action capacity, it was determined that a new model should be adopted by AISC for prying action of single-angles because the current prying equations do not accurately predict the behavior for single-angle connections. The British Steel Construction Institute P212 publication presents a large displacement analysis method in its Appendix D for determining the effects of prying action on bolt strength for double angle connections.  In this thesis, that model has been altered for single-angles and reasonably predicts the capacity of the tested connection by determining a reduced bolt stress.  Therefore an equation for the limit state of bolt tensile failure with prying action for single-angles has been proposed to be adopted by AISC for connections with angle thickness of 5/8-in or less. Typically, simple-shear connections such as single-angles are relatively flexible and therefore more research should be conducted on flexible bolted connections where prying action would occur.'},
                          indicator1='3')

    def test_create_marc_record_699(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_categorization>
                          <DISS_keyword>bolted connections, finite element, prying action, shear connections, single angle, structural integrity</DISS_keyword>
                        </DISS_categorization>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['699'], {
            'a': 'bolted connections; finite element; prying action; shear connections; single angle; structural integrity.'},
                          indicator1='0', indicator2='4')

    def test_create_marc_record_245(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_title>Tensile Capacity of Single-Angle Shear Connections Considering Prying Action.</DISS_title>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['245'], {
            'a': 'Tensile Capacity of Single-Angle Shear Connections Considering Prying Action',
            'h': '[electronic resource].'},
                          indicator1='1', indicator2='0')

    def test_create_marc_record_245_quotes(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_title>Tensile Capacity of "Single-Angle Shear Connections" Considering 'Prying Action'</DISS_title>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['245'], {
            'a': 'Tensile Capacity of Single-Angle Shear Connections Considering Prying Action',
            'h': '[electronic resource].'},
                          indicator1='1', indicator2='0')

    def test_create_marc_record_245_upper(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_title>TENSILE CAPACITY OF SINGLE-ANGLE SHEAR CONNECTIONS CONSIDERING PRYING ACTION</DISS_title>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['245'], {
            'a': 'Tensile Capacity Of Single-Angle Shear Connections Considering Prying Action',
            'h': '[electronic resource].'},
                          indicator1='1', indicator2='0')

    def test_create_marc_record_245_leading_article(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_title>The Tensile Capacity of Single-Angle Shear Connections Considering Prying Action</DISS_title>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['245'], {
            'a': 'The Tensile Capacity of Single-Angle Shear Connections Considering Prying Action',
            'h': '[electronic resource].'},
                          indicator1='1', indicator2='4')

    def test_create_marc_record_245_subtitle(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_title>Tensile Capacity of Single-Angle Shear Connections Considering Prying Action: The Real Story</DISS_title>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['245'], {
            'a': 'Tensile Capacity of Single-Angle Shear Connections Considering Prying Action',
            'b': 'The Real Story',
            'h': '[electronic resource]: '},
                          indicator1='1', indicator2='0')

    def test_create_marc_record_710(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_institution>
                          <DISS_inst_contact>Civil Engineering</DISS_inst_contact>
                        </DISS_institution>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['710'], {
            'a': 'George Washington University.',
            'b': 'Civil Engineering.'},
                          indicator1='2')

    def test_create_marc_record_500(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_dates>
                            <DISS_comp_date>2011</DISS_comp_date>
                            <DISS_accept_date>01/01/2011</DISS_accept_date>
                        </DISS_dates>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['500'], {
            'a': 'Title and description based on DISS metadata (ProQuest UMI) as of 01/01/2011.'
        })

    def test_create_marc_record_502(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_dates>
                            <DISS_comp_date>2011</DISS_comp_date>
                            <DISS_accept_date>01/01/2011</DISS_accept_date>
                        </DISS_dates>
                        <DISS_degree>M.S.</DISS_degree>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['502'], {
            'a': 'Thesis',
            'b': '(M.S.)--',
            'c': 'George Washington University,',
            'd': '2011.'
        })

    def test_create_marc_record_264(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_dates>
                            <DISS_comp_date>2011</DISS_comp_date>
                            <DISS_accept_date>01/01/2011</DISS_accept_date>
                        </DISS_dates>
                    </DISS_description>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['264'], {
            'a': '[Washington, D. C.] :',
            'b': 'George Washington University,',
            'c': '2011.'
        }, indicator1='3', indicator2='0')

    def test_create_marc_record_100_700(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_authorship>
                        <DISS_author type="primary">
                            <DISS_name>
                                <DISS_surname>Blass</DISS_surname>
                                <DISS_fname>Deborah</DISS_fname>
                                <DISS_middle>A.</DISS_middle>
                                <DISS_suffix/>
                                <DISS_affiliation>George Washington University</DISS_affiliation>
                            </DISS_name>
                        </DISS_author>
                    </DISS_authorship>
                    <DISS_authorship>
                        <DISS_author type="secondary">
                            <DISS_name>
                                <DISS_surname>Kaufman</DISS_surname>
                                <DISS_fname>Annette</DISS_fname>
                                <DISS_middle />
                                <DISS_suffix/>
                                <DISS_affiliation>George Washington University</DISS_affiliation>
                            </DISS_name>
                        </DISS_author>
                    </DISS_authorship>
                </DISS_submission>
            """)
        record = self.loader._create_marc_record(metadata_tree, 'Blass_gwu_0075M_11053_DATA', "http://repo/11053")
        self.assert_field(record['100'], {
            'a': 'Blass, Deborah A.',
        }, indicator2='1')
        self.assert_field(record['700'], {
            'a': 'Kaufman, Annette.',
        }, indicator2='1')

    # TODO: Test 008

    def test_create_repo_metadata_creator_and_contributor(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_authorship>
                        <DISS_author type="primary">
                            <DISS_name>
                                <DISS_surname>Blass</DISS_surname>
                                <DISS_fname>Deborah</DISS_fname>
                                <DISS_middle>A.</DISS_middle>
                                <DISS_suffix/>
                                <DISS_affiliation>George Washington University</DISS_affiliation>
                            </DISS_name>
                        </DISS_author>
                    </DISS_authorship>
                    <DISS_authorship>
                        <DISS_author type="secondary">
                            <DISS_name>
                                <DISS_surname>Kaufman</DISS_surname>
                                <DISS_fname>Annette</DISS_fname>
                                <DISS_middle />
                                <DISS_suffix/>
                                <DISS_affiliation>George Washington University</DISS_affiliation>
                            </DISS_name>
                        </DISS_author>
                    </DISS_authorship>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('Blass, Deborah A.', repo_metadata['creator'])
        self.assertEqual(['Kaufman, Annette'], repo_metadata['contributor'])

    def test_create_repo_metadata_date_created(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_dates>
                            <DISS_comp_date>2011</DISS_comp_date>
                        </DISS_dates>
                    </DISS_description>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('2011', repo_metadata['date_created'])

    def test_create_repo_metadata_keyword(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_categorization>
                          <DISS_keyword>bolted connections, finite element, prying action, shear connections, single angle, structural integrity</DISS_keyword>
                        </DISS_categorization>
                    </DISS_description>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual(['bolted connections',
                          'finite element',
                          'prying action',
                          'shear connections',
                          'single angle',
                          'structural integrity'], repo_metadata['keyword'])

    def test_create_repo_metadata_language(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_categorization>
                            <DISS_language>en</DISS_language>
                        </DISS_categorization>
                    </DISS_description>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('en', repo_metadata['language'])

    def test_create_repo_metadata_title(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_title>Tensile Capacity of Single-Angle Shear Connections Considering Prying Action</DISS_title>
                    </DISS_description>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('Tensile Capacity of Single-Angle Shear Connections Considering Prying Action',
                         repo_metadata['title'])

    def test_create_repo_metadata_description(self):
        # TODO: Need example of HTML markup to test.
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_content>
                        <DISS_abstract>
                          <DISS_para>After the attacks on the World Trade Centers on September 11, 2001, engineers agreed that work needed to be done to increase the robustness of structures.  Research has increased in many areas including progressive collapse of structures, structural response to fires, and other effects of extreme loading conditions.  As a result of this research, building codes have been altered to include increased protection against these events.  One newly implemented structural integrity provision for the 2009 International Building Code (IBC) includes the need to provide a minimum tensile capacity in simple shear steel connections.</DISS_para>
                          <DISS_para>This thesis is a continuation of a previously started project by the Department of Civil and Environmental Engineering at George Washington University for the American Institute of Steel Construction.  The work included experimental testing of simple shear all-bolted single-angle connections to determine the failure mechanism and ultimate strength.  The single-angle connection is one of the most economical and widely used simple shear connections in buildings and therefore testing was undertaken to ensure that these connections would comply with the new structural integrity provisions.  The angles failed due to two mechanisms: bolt tensile failure and shear fracture of the angle.</DISS_para>
                          <DISS_para>Based on the results of the single-angle experiments, a finite-element model was created in order to investigate an interesting outcome regarding the prying action of the single-angle connection tests. The observed strength is about three times larger than the current AISC prying equations predict, which is overly conservative.  The AISC prying equations are largely based on research which involved relatively rigid symmetrical tee-sections so the behavior of relatively flexible single-angles would be expectantly different. </DISS_para>
                          <DISS_para>Prior to the single-angle tests, there is very minimal published research on single-angles under tensile load.  The test data supporting the AISC prying equations was mostly based on less flexible connections.  Prying action involves a complex interaction between tensile, shear, and moments that occurs more so when elements are flexible and able to have large deformations, effectively causing an increase in the load on the bolts.  </DISS_para>
                          <DISS_para>Following the finite-element model and a study of different methods for calculating the prying action capacity, it was determined that a new model should be adopted by AISC for prying action of single-angles because the current prying equations do not accurately predict the behavior for single-angle connections. The British Steel Construction Institute P212 publication presents a large displacement analysis method in its Appendix D for determining the effects of prying action on bolt strength for double angle connections.  In this thesis, that model has been altered for single-angles and reasonably predicts the capacity of the tested connection by determining a reduced bolt stress.  Therefore an equation for the limit state of bolt tensile failure with prying action for single-angles has been proposed to be adopted by AISC for connections with angle thickness of 5/8-in or less. Typically, simple-shear connections such as single-angles are relatively flexible and therefore more research should be conducted on flexible bolted connections where prying action would occur.</DISS_para>
                        </DISS_abstract>
                    </DISS_content>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('After the attacks on the World Trade Centers on September 11, 2001, engineers agreed that work needed to be done to increase the robustness of structures.  Research has increased in many areas including progressive collapse of structures, structural response to fires, and other effects of extreme loading conditions.  As a result of this research, building codes have been altered to include increased protection against these events.  One newly implemented structural integrity provision for the 2009 International Building Code (IBC) includes the need to provide a minimum tensile capacity in simple shear steel connections.This thesis is a continuation of a previously started project by the Department of Civil and Environmental Engineering at George Washington University for the American Institute of Steel Construction.  The work included experimental testing of simple shear all-bolted single-angle connections to determine the failure mechanism and ultimate strength.  The single-angle connection is one of the most economical and widely used simple shear connections in buildings and therefore testing was undertaken to ensure that these connections would comply with the new structural integrity provisions.  The angles failed due to two mechanisms: bolt tensile failure and shear fracture of the angle.Based on the results of the single-angle experiments, a finite-element model was created in order to investigate an interesting outcome regarding the prying action of the single-angle connection tests. The observed strength is about three times larger than the current AISC prying equations predict, which is overly conservative.  The AISC prying equations are largely based on research which involved relatively rigid symmetrical tee-sections so the behavior of relatively flexible single-angles would be expectantly different. Prior to the single-angle tests, there is very minimal published research on single-angles under tensile load.  The test data supporting the AISC prying equations was mostly based on less flexible connections.  Prying action involves a complex interaction between tensile, shear, and moments that occurs more so when elements are flexible and able to have large deformations, effectively causing an increase in the load on the bolts.  Following the finite-element model and a study of different methods for calculating the prying action capacity, it was determined that a new model should be adopted by AISC for prying action of single-angles because the current prying equations do not accurately predict the behavior for single-angle connections. The British Steel Construction Institute P212 publication presents a large displacement analysis method in its Appendix D for determining the effects of prying action on bolt strength for double angle connections.  In this thesis, that model has been altered for single-angles and reasonably predicts the capacity of the tested connection by determining a reduced bolt stress.  Therefore an equation for the limit state of bolt tensile failure with prying action for single-angles has been proposed to be adopted by AISC for connections with angle thickness of 5/8-in or less. Typically, simple-shear connections such as single-angles are relatively flexible and therefore more research should be conducted on flexible bolted connections where prying action would occur.',
                         repo_metadata['description'])

    def test_create_repo_metadata_gw_affiliation(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_institution>
                          <DISS_inst_contact>Civil Engineering</DISS_inst_contact>
                        </DISS_institution>
                    </DISS_description>
                </DISS_submission>
            """)

        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('Civil Engineering', repo_metadata['gw_affiliation'])

    def test_create_repo_metadata_degree(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_description page_count="97" type="masters" external_id="http://dissertations.umi.com/gwu:11053" apply_for_copyright="yes">
                        <DISS_degree>M.S.</DISS_degree>
                    </DISS_description>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('M.S.', repo_metadata['degree'])

    def test_create_repo_metadata_embargo(self):
        metadata_tree = ElementTree.fromstring(
            """<?xml version="1.0" encoding="UTF-8"?>
                <DISS_submission publishing_option="0" embargo_code="0" third_party_search="N">
                    <DISS_restriction>
                        <DISS_sales_restriction code="1" remove="11/20/2015"/>
                    </DISS_restriction>
                </DISS_submission>
            """)
        repo_metadata = self.loader.create_repository_metadata(metadata_tree)
        self.assertEqual('2015-11-20', repo_metadata['embargo_date'])


class IdStoreTest(TestCase):
    def setUp(self):
        self.db_filepath = './id.db'

    def tearDown(self):
        if os.path.exists(self.db_filepath):
            os.remove(self.db_filepath)

    def test_id_store(self):
        with IdStore() as store:
            self.assertEqual(0, len(list(store)))
            store['etd_id1'] = 'repository_id1'
            self.assertEqual(1, len(list(store)))
            self.assertEqual(store['etd_id1'], 'repository_id1')

            store['etd_id2'] = 'repository_id2'
            self.assertEqual(2, len(list(store)))
            self.assertEqual(store['etd_id2'], 'repository_id2')

            store['etd_id1'] = 'repository_id1.1'
            self.assertEqual(2, len(list(store)))
            self.assertEqual(store['etd_id1'], 'repository_id1.1')
