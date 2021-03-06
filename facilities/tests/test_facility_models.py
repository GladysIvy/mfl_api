from __future__ import division

from rest_framework.exceptions import ValidationError
from model_mommy import mommy

from common.tests.test_models import BaseTestCase
from common.models import (
    Contact,
    Ward,
    PhysicalAddress,
    ContactType,
    County,
    Constituency,
    Town
)

from ..models import (
    OwnerType,
    Owner,
    JobTitle,
    Officer,
    OfficerContact,
    FacilityStatus,
    FacilityType,
    RegulatingBody,
    RegulationStatus,
    Facility,
    FacilityRegulationStatus,
    FacilityContact,
    FacilityUnit,
    FacilityServiceRating,
    ServiceCategory,
    Service,
    ServiceOption,
    FacilityService,
    FacilityApproval,
    FacilityOperationState,
    RegulatingBodyContact,
    Option
)


class TestFacilityOperationState(BaseTestCase):

    def test_save(self):
        status = mommy.make(FacilityStatus, name='PENDING_OPENING')
        facility = mommy.make(
            Facility, name='Nai hosi', operation_status=status)
        status_2 = mommy.make(FacilityStatus, name='OPERATIONAL')
        facility_operation_state = mommy.make(
            FacilityOperationState, facility=facility,
            operation_status=status_2)
        self.assertEquals(1, FacilityOperationState.objects.count())
        self.assertEquals(facility_operation_state.facility, facility)


class TestServiceCategory(BaseTestCase):

    def test_unicode(self):
        instance = ServiceCategory(name='test name')
        self.assertEqual(str(instance), 'test name')


class TestOption(BaseTestCase):

    def test_unicode(self):
        instance = Option(option_type='BOOLEAN', display_text='Yes/No')
        self.assertEqual(str(instance), 'BOOLEAN: Yes/No')


class TestServiceOption(BaseTestCase):

    def test_unicode(self):
        service = Service(name='savis')
        option = Option(option_type='BOOLEAN', display_text='Yes/No')
        service_option = ServiceOption(service=service, option=option)
        self.assertEqual(str(service_option), 'savis: BOOLEAN: Yes/No')


class TestFacilityService(BaseTestCase):

    def test_unicode(self):
        facility = Facility(name='thifitari')
        service = Service(name='savis')
        option = Option(option_type='BOOLEAN', display_text='Yes/No')
        service_option = ServiceOption(service=service, option=option)
        facility_service = FacilityService(
            facility=facility, selected_option=service_option)
        self.assertEqual(
            str(facility_service), 'thifitari: savis: BOOLEAN: Yes/No')
        self.assertEquals('Yes/No', facility_service.option_display_value)
        self.assertEquals('savis', facility_service.service_name)

    def test_facility_service(self):
        facility = mommy.make(Facility, name='thifitari')
        service_category = mommy.make(ServiceCategory, name='a good service')
        service = mommy.make(Service, name='savis', category=service_category)
        option = mommy.make(
            Option, option_type='BOOLEAN', display_text='Yes/No')
        service_option = mommy.make(
            ServiceOption, service=service, option=option)
        facility_service = mommy.make(
            FacilityService, facility=facility, selected_option=service_option
        )
        expected_data = [
            {
                "id": facility_service.id,
                "service_id": service.id,
                "service_name": service.name,
                "option_name": option.display_text,
                "category_name": service_category.name,
                "category_id": service_category.id,
                "average_rating": facility_service.average_rating
            }
        ]
        self.assertEquals(expected_data, facility.get_facility_services)

    def test_average_rating(self):
        facility1 = mommy.make(Facility)
        service1, service2 = mommy.make(Service), mommy.make(Service)
        soption1, soption2 = (
            mommy.make(ServiceOption, service=service1),
            mommy.make(ServiceOption, service=service2)
        )
        fs1, fs2 = (
            mommy.make(
                FacilityService, facility=facility1, selected_option=soption1
            ),
            mommy.make(
                FacilityService, facility=facility1, selected_option=soption2
            )
        )
        fs1_ratings = [
            mommy.make(FacilityServiceRating, rating=2, facility_service=fs1),
            mommy.make(FacilityServiceRating, rating=3, facility_service=fs1),
            mommy.make(FacilityServiceRating, rating=4, facility_service=fs1),
        ]
        fs2_ratings = [
            mommy.make(FacilityServiceRating, rating=4, facility_service=fs2),
            mommy.make(FacilityServiceRating, rating=3, facility_service=fs2),
            mommy.make(FacilityServiceRating, rating=4, facility_service=fs2),
        ]

        # add some noise
        facility2 = mommy.make(Facility)
        service3, service4 = mommy.make(Service), mommy.make(Service)
        soption3, soption4 = (
            mommy.make(ServiceOption, service=service3),
            mommy.make(ServiceOption, service=service4)
        )
        fs3, fs4 = (
            mommy.make(
                FacilityService, facility=facility2, selected_option=soption3
            ),
            mommy.make(
                FacilityService, facility=facility2, selected_option=soption4
            )
        )

        mommy.make(FacilityServiceRating, rating=2, facility_service=fs3),
        mommy.make(FacilityServiceRating, rating=3, facility_service=fs3),
        mommy.make(FacilityServiceRating, rating=4, facility_service=fs3),
        mommy.make(FacilityServiceRating, rating=4, facility_service=fs4),
        mommy.make(FacilityServiceRating, rating=3, facility_service=fs4),
        mommy.make(FacilityServiceRating, rating=4, facility_service=fs4),

        # test calculations
        self.assertEqual(
            fs1.average_rating,
            sum([i.rating for i in fs1_ratings]) / len(fs1_ratings)
        )
        self.assertEqual(
            fs2.average_rating,
            sum([i.rating for i in fs2_ratings]) / len(fs2_ratings)
        )
        self.assertEqual(
            facility1.average_rating,
            (fs1.average_rating + fs2.average_rating) / 2
        )


class TestServiceModel(BaseTestCase):

    def test_save_without_code(self):
        service = mommy.make(Service, name='some name')
        self.assertEquals(1, Service.objects.count())

        # test unicode
        self.assertEquals('some name', service.__unicode__())

    def test_save_with_code(self):
        service = mommy.make(Service, code='1341')
        self.assertEquals(1341, service.code)

    def test_service_category_name(self):
        category = mommy.make(ServiceCategory)
        service = mommy.make(Service, category=category)
        self.assertEquals(category.name, service.category_name)


class TestOwnerTypes(BaseTestCase):

    def test_save(self):
        data = {
            "name": "FBO",
            "description": "The the faith based organisation owners"
        }
        data = self.inject_audit_fields(data)
        owner_type = OwnerType.objects.create(**data)
        self.assertEquals(1, OwnerType.objects.count())

        # test unicode
        self.assertEquals("FBO", owner_type.__unicode__())


class TestOwnerModel(BaseTestCase):

    def test_save(self):
        owner_type = mommy.make(OwnerType, name="FBO")
        data = {
            "owner_type": owner_type,
            "name": "CHAK",
            "description": "this is some description",
            "abbreviation": "CHAK"
        }
        data = self.inject_audit_fields(data)
        owner = Owner.objects.create(**data)
        self.assertEquals(1, Owner.objects.count())

        owner_with_no_code = mommy.make(Owner, code=None)
        self.assertTrue(owner_with_no_code.code >= 1)

        owner_with_code = mommy.make(Owner, code=679879)
        self.assertTrue(owner_with_code.code >= 1)

        # test unicode
        self.assertEquals("CHAK", owner.__unicode__())
        self.assertIsNotNone(owner.code)

    def test_owner_code_sequence(self):
        # make code none so that mommy does not supply it
        owner_1 = mommy.make(Owner, code=None)
        owner_2 = mommy.make(Owner, code=None)
        owner_2_code = int(owner_1.code) + 1
        self.assertEquals(owner_2.code, owner_2_code)


class TestJobTitleModel(BaseTestCase):

    def test_save(self):
        data = {
            "name": "Nurse officer incharge",
            "description": "some good description"
        }
        data = self.inject_audit_fields(data)
        jt = JobTitle.objects.create(**data)
        self.assertEquals(1, JobTitle.objects.count())

        # test unicode
        self.assertEquals("Nurse officer incharge", jt.__unicode__())


class TestOfficer(BaseTestCase):

    def test_save(self):
        jt = mommy.make(JobTitle, name='Nursing officer incharge')
        data = {
            "name": "Kimani Maruge",
            "registration_number": "78736790",
            "job_title": jt
        }
        data = self.inject_audit_fields(data)
        officer = Officer.objects.create(**data)
        self.assertEquals(1, Officer.objects.count())

        # test unicode
        self.assertEquals("Kimani Maruge", officer.__unicode__())


class TestOfficerContactModel(BaseTestCase):

    def test_save(self):
        officer = mommy.make(Officer, name='Maruge')
        contact = mommy.make(Contact, contact='maruge@gmail.com')
        data = {
            "officer": officer,
            "contact": contact
        }
        data = self.inject_audit_fields(data)
        contact = OfficerContact.objects.create(**data)
        self.assertEquals(1, OfficerContact.objects.count())

        # test unicode
        expected = "Maruge: maruge@gmail.com"
        self.assertEquals(expected, contact.__unicode__())


class TestFacilityStatusModel(BaseTestCase):

    def test_save(self):
        data = {
            "name": "OPERATIONAL",
            "description": "The Facility is operating normally"
        }
        data = self.inject_audit_fields(data)
        fs = FacilityStatus.objects.create(**data)

        # test unicode
        self.assertEquals('OPERATIONAL', fs.__unicode__())


class TestFacilityTypeModel(BaseTestCase):

    def test_save(self):
        data = {
            "name": "Hospital",
            "sub_division": "District Hospital"
        }
        data = self.inject_audit_fields(data)
        facility_type = FacilityType.objects.create(**data)
        self.assertEquals(1, FacilityType.objects.count())

        # test unicode
        self.assertEquals("Hospital", facility_type.__unicode__())


class TestRegulatingBodyModel(BaseTestCase):

    def test_save(self):
        data = {
            "name": "Director of Medical Services",
            "abbreviation": "DMS",
            "regulation_verb": "Gazette"
        }
        data = self.inject_audit_fields(data)
        regulating_body = RegulatingBody.objects.create(**data)
        self.assertEquals(1, RegulatingBody.objects.count())

        # test unicode
        self.assertEquals(
            "Director of Medical Services",
            regulating_body.__unicode__())

    def test_regulating_body_postal_address(self):
        postal = mommy.make(ContactType, name='POSTAL')
        contact = mommy.make(Contact, contact_type=postal)
        regulating_body = mommy.make(RegulatingBody, name='KMPDB')
        mommy.make(
            RegulatingBodyContact, regulating_body=regulating_body,
            contact=contact)
        self.assertEquals(contact, regulating_body.postal_address.contact)


class TestFacility(BaseTestCase):

    def test_save(self):
        facility_type = mommy.make(FacilityType, name="DISPENSARY")
        operation_status = mommy.make(FacilityStatus, name="OPERATIONAL")
        officer_in_charge = mommy.make(Officer, name='Dr Burmuriat')
        regulating_body = mommy.make(RegulatingBody, name='KMPDB')
        owner = mommy.make(Owner, name="MOH")
        ward = mommy.make(Ward)
        address = mommy.make(PhysicalAddress)
        data = {
            "name": "Forces Memorial",
            "description": "Hospital for the armed forces",
            "facility_type": facility_type,
            "number_of_beds": 100,
            "number_of_cots": 1,
            "open_whole_day": True,
            "open_whole_week": True,
            "operation_status": operation_status,
            "ward": ward,
            "owner": owner,
            "location_desc": "it is located along Moi Avenue Nairobi",
            "officer_in_charge": officer_in_charge,
            "physical_address": address
        }
        data = self.inject_audit_fields(data)
        facility = Facility.objects.create(**data)
        facility_reg_status = mommy.make(
            FacilityRegulationStatus, facility=facility,
            regulating_body=regulating_body, is_confirmed=True)
        self.assertEquals(1, Facility.objects.count())

        # Bloody branch misses
        mommy.make(Facility, code=89778)
        mommy.make(Facility, code=None)

        #  test unicode
        self.assertEquals("Forces Memorial", facility.__unicode__())
        self.assertIsNotNone(facility.code)
        self.assertEquals(
            facility_reg_status,
            facility.current_regulatory_status)

    def test_working_of_facility_code_sequence(self):
        # make code none so that mommy does not supply it
        facility_1 = mommy.make(Facility, code=None)
        facility_2 = mommy.make(Facility, code=None)
        facility_2_code = int(facility_1.code) + 1
        self.assertEquals(int(facility_2.code), facility_2_code)

    def test_facility_not_approved(self):
        facility = mommy.make(Facility)
        self.assertFalse(facility.is_approved)

    def test_facility_approved(self):
        facility = mommy.make(Facility)
        facility_approval = mommy.make(
            FacilityApproval,
            facility=facility,
            comment='It meets all the registration requirements')
        self.assertTrue(facility.is_approved)
        self.assertEquals(facility, facility_approval.facility)
        self.assertEquals(
            facility_approval.comment,
            'It meets all the registration requirements')

    def test_county(self):
        county = mommy.make(County)
        constituency = mommy.make(Constituency, county=county)
        ward = mommy.make(Ward, constituency=constituency)
        facility = mommy.make(Facility, ward=ward)
        self.assertEquals(county.name, facility.county)

    def test_constituency(self):
        county = mommy.make(County)
        constituency = mommy.make(Constituency, county=county)
        ward = mommy.make(Ward, constituency=constituency)
        facility = mommy.make(Facility, ward=ward)
        self.assertEquals(constituency.name, facility.constituency)

    def test_operations_status_name(self):
        operation_status = mommy.make(FacilityStatus)
        facility = mommy.make(Facility, operation_status=operation_status)
        self.assertEquals(
            facility.operation_status_name, operation_status.name)

    def test_regulatory_status_name(self):
        facility = mommy.make(Facility)
        facility_reg_status = mommy.make(
            FacilityRegulationStatus, facility=facility, is_confirmed=True)
        self.assertEquals(
            facility.regulatory_status_name,
            facility_reg_status.regulation_status.name)

    def test_owner_type_name(self):
        owner_type = mommy.make(OwnerType, name='GAVA')
        owner = mommy.make(Owner, owner_type=owner_type)
        facility = mommy.make(Facility, owner=owner)
        self.assertEquals(owner.name, facility.owner_name)

    def test_owner_name(self):
        owner_type = mommy.make(OwnerType, name='GAVA')
        owner = mommy.make(Owner, owner_type=owner_type)
        facility = mommy.make(Facility, owner=owner)
        self.assertEquals(owner_type.name, facility.owner_type_name)

    def test_facility_type_name(self):
        facility_type = mommy.make(FacilityType, name='District')
        facility = mommy.make(Facility, facility_type=facility_type)
        self.assertEquals(facility.facility_type_name, facility_type.name)

    def test_is_regulated_is_true(self):
        facility = mommy.make(Facility)
        mommy.make(
            FacilityRegulationStatus, is_confirmed=True, facility=facility)
        self.assertTrue(facility.is_regulated)

    def test_is_regulated_is_false(self):
        facility = mommy.make(Facility)
        mommy.make(
            FacilityRegulationStatus, is_confirmed=False, facility=facility)
        self.assertFalse(facility.is_regulated)

    def test_publishing(self):
        with self.assertRaises(ValidationError):
            mommy.make(Facility, is_published=True)

    def test_facility_get_properties(self):
        town = mommy.make(Town, name='Londiani')
        physical_address = mommy.make(PhysicalAddress, town=town)
        county = mommy.make(County, name='Bomet')
        constituency = mommy.make(Constituency, county=county, name='Pokot')
        ward = mommy.make(Ward, name='Chepalungu', constituency=constituency)
        facility = mommy.make(
            Facility, ward=ward, physical_address=physical_address)

        # test county
        self.assertEquals('Bomet', facility.get_county)
        self.assertEquals('Pokot', facility.get_constituency)
        self.assertEquals('Chepalungu', facility.ward_name)
        self.assertEquals(
            {
                "id": physical_address.id,
                "town": town.name,
                "plot_number": physical_address.plot_number,
                "nearest_landmark": physical_address.nearest_landmark,
                "address": physical_address.address,
                "postal_code": physical_address.postal_code
            }, facility.facility_physical_address)


class TestFacilityContact(BaseTestCase):

    def test_save(self):
        contact_type = mommy.make(ContactType)
        facility = mommy.make(
            Facility, name="Nairobi Hospital")
        contact = mommy.make(
            Contact, contact="075689267", contact_type=contact_type)
        data = {
            "facility": facility,
            "contact": contact
        }
        data = self.inject_audit_fields(data)
        facility_contact = FacilityContact.objects.create(**data)

        # test unicode
        expected = "Nairobi Hospital: 075689267"
        self.assertEquals(expected, facility_contact.__unicode__())
        expected_data = [
            {
                "id": facility_contact.id,
                "contact_id": contact.id,
                "contact": contact.contact,
                "contact_type_name": contact_type.name
            }
        ]
        self.assertEquals(expected_data, facility.get_facility_contacts)


class TestRegulationStatus(BaseTestCase):

    def test_save(self):
        data = {
            "name": "OPERATIONAL",
            "description": "The facility is operating normally."
        }
        data = self.inject_audit_fields(data)
        regulation_status = RegulationStatus.objects.create(**data)
        self.assertEquals(1, RegulationStatus.objects.count())

        # test unicode
        self.assertEquals("OPERATIONAL", regulation_status.__unicode__())


class TestFacilityRegulationStatus(BaseTestCase):

    def test_save(self):
        facility = mommy.make(Facility, name="Nairobi Hospital")
        status = mommy.make(RegulationStatus, name="SUSPENDED")
        regulator = mommy.make(RegulatingBody, name='KMPDB')
        data = {
            "facility": facility,
            "regulation_status": status,
            "reason": "Reports of misconduct by the doctor",
            "regulating_body": regulator
        }
        data = self.inject_audit_fields(data)
        facility_reg_status = FacilityRegulationStatus.objects.create(**data)
        self.assertEquals(1, FacilityRegulationStatus.objects.count())

        #  test unicode
        expected = "Nairobi Hospital: SUSPENDED"
        self.assertEquals(expected, facility_reg_status.__unicode__())


class TestFacilityUnitModel(BaseTestCase):

    def test_string_representation(self):
        facility = mommy.make(Facility, name='AKUH')
        data = {
            "facility": facility,
            "name": "Pharmacy",
            "description": "This is the AKUH Pharmacy section."
        }
        data = self.inject_audit_fields(data)
        facility_unit = FacilityUnit.objects.create(**data)
        self.assertEquals(1, FacilityUnit.objects.count())
        self.assertEquals(str(facility_unit), 'AKUH: Pharmacy')


class TestRegulationStatusModel(BaseTestCase):

    def test_save(self):
        mommy.make(RegulationStatus)
        self.assertEquals(1, RegulationStatus.objects.count())

    def test_validate_only_one_initial_state(self):
        mommy.make(
            RegulationStatus, is_initial_state=True, is_final_state=False)
        with self.assertRaises(ValidationError):
            mommy.make(
                RegulationStatus, is_initial_state=True, is_final_state=False)

    def test_only_one_final_state(self):
        mommy.make(RegulationStatus, is_final_state=True)
        with self.assertRaises(ValidationError):
            mommy.make(RegulationStatus, is_final_state=True)

    def test_previous_state_name(self):
        status = mommy.make(RegulationStatus, is_final_state=True)
        prev_state = mommy.make(RegulationStatus, previous_status=status)
        self.assertEquals(status.name, prev_state.previous_state_name)

    def test_next_state_name(self):
        status = mommy.make(RegulationStatus, is_initial_state=True)
        next_state = mommy.make(RegulationStatus, next_status=status)
        self.assertEquals(status.name, next_state.next_state_name)

    def test_previous_state_name_is_null(self):
        status = mommy.make(RegulationStatus, is_initial_state=True)
        self.assertEquals("", status.previous_state_name)

    def test_next_state_name_is_null(self):
        status = mommy.make(RegulationStatus, is_final_state=True)
        self.assertEquals("", status.next_state_name)


class TestFacilityServiceRating(BaseTestCase):

    def test_unicode(self):
        facility = mommy.make(Facility, name='fac')
        service = mommy.make(Service, name='serv')
        soption = mommy.make(ServiceOption, service=service)
        facility_service = mommy.make(
            FacilityService, facility=facility, selected_option=soption
        )
        rating = mommy.make(
            FacilityServiceRating, facility_service=facility_service,
            rating=5
        )
        self.assertEqual(str(rating), "serv (fac): 5")
