"""
E2B R3 ICSR XML Generator Module
Generates E2B R3 ICSR XML in HL7 format from JSON data.
"""

from lxml import etree
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
from .mapping_parser import MappingParser
from .data_extractor import DataExtractor


class ICSRXMLGenerator:
    """
    Generates E2B R3 ICSR XML documents in HL7 format.

    E2B R3 is based on HL7 v3 messaging standard and follows
    the ICH International Conference on Harmonisation guidelines.
    """

    # HL7 and E2B namespaces
    NAMESPACES = {
        None: "urn:hl7-org:v3",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    def __init__(self, mapping_parser: MappingParser):
        """
        Initialize the XML generator.

        Args:
            mapping_parser: MappingParser instance with E2B to JSON mappings
        """
        self.mapper = mapping_parser
        self.nsmap = self.NAMESPACES

    def generate(self, extractor: DataExtractor, message_id: Optional[str] = None) -> etree.Element:
        """
        Generate the complete E2B R3 ICSR XML document.

        Args:
            extractor: DataExtractor instance with JSON data
            message_id: Optional message ID (generated if not provided)

        Returns:
            lxml Element representing the complete XML document
        """
        # Create root element - MCCI_IN200100UV01 is the main ICSR message type
        root = etree.Element(
            "MCCI_IN200100UV01",
            nsmap=self.nsmap,
            ITSVersion="XML_1.0"
        )

        # Add schema location
        root.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "urn:hl7-org:v3 MCCI_IN200100UV01.xsd"
        )

        # Add message ID
        msg_id = message_id or str(uuid.uuid4())
        id_elem = etree.SubElement(root, "id")
        id_elem.set("extension", msg_id)
        id_elem.set("root", "2.16.840.1.113883.3.989.2.1.3.1")

        # Add creation time
        creation_time = etree.SubElement(root, "creationTime")
        creation_time.set("value", datetime.utcnow().strftime("%Y%m%d%H%M%S"))

        # Add interaction ID
        interaction_id = etree.SubElement(root, "interactionId")
        interaction_id.set("extension", "MCCI_IN200100UV01")
        interaction_id.set("root", "2.16.840.1.113883.1.6")

        # Add processing code
        processing_code = etree.SubElement(root, "processingCode")
        processing_code.set("code", "P")

        # Add processing mode code
        processing_mode = etree.SubElement(root, "processingModeCode")
        processing_mode.set("code", "T")

        # Add accept ack code
        accept_ack = etree.SubElement(root, "acceptAckCode")
        accept_ack.set("code", "AL")

        # Add receiver
        self._add_receiver(root)

        # Add sender
        self._add_sender(root, extractor)

        # Add control act process (main content)
        self._add_control_act_process(root, extractor)

        return root

    def _add_receiver(self, parent: etree.Element):
        """Add receiver information to the message."""
        receiver = etree.SubElement(parent, "receiver")
        receiver.set("typeCode", "RCV")

        device = etree.SubElement(receiver, "device")
        device.set("classCode", "DEV")
        device.set("determinerCode", "INSTANCE")

        device_id = etree.SubElement(device, "id")
        device_id.set("extension", "RECEIVER")
        device_id.set("root", "2.16.840.1.113883.3.989.2.1.3.2")

    def _add_sender(self, parent: etree.Element, extractor: DataExtractor):
        """Add sender information to the message."""
        sender = etree.SubElement(parent, "sender")
        sender.set("typeCode", "SND")

        device = etree.SubElement(sender, "device")
        device.set("classCode", "DEV")
        device.set("determinerCode", "INSTANCE")

        device_id = etree.SubElement(device, "id")
        device_id.set("extension", "SENDER")
        device_id.set("root", "2.16.840.1.113883.3.989.2.1.3.3")

    def _add_control_act_process(self, parent: etree.Element, extractor: DataExtractor):
        """
        Add the control act process element containing the actual ICSR data.
        """
        control_act = etree.SubElement(parent, "controlActProcess")
        control_act.set("classCode", "CACT")
        control_act.set("moodCode", "EVN")

        # Add code
        code = etree.SubElement(control_act, "code")
        code.set("code", "PORR_TE049018UV")
        code.set("codeSystem", "2.16.840.1.113883.1.18")

        # Add subject containing the ICSR document
        subject = etree.SubElement(control_act, "subject")
        subject.set("typeCode", "SUBJ")

        # Add the actual ICSR investigation event
        self._add_investigation_event(subject, extractor)

    def _add_investigation_event(self, parent: etree.Element, extractor: DataExtractor):
        """Add the investigation event (main ICSR content)."""
        investigation = etree.SubElement(parent, "investigationEvent")
        investigation.set("classCode", "INVSTG")
        investigation.set("moodCode", "EVN")

        # Add investigation ID
        inv_id = etree.SubElement(investigation, "id")
        case_id = extractor.extract("pv_case.identifier") or "UNKNOWN"
        inv_id.set("extension", case_id)
        inv_id.set("root", "2.16.840.1.113883.3.989.2.1.3.4")

        # Add code
        code = etree.SubElement(investigation, "code")
        code.set("code", "PAT_ADV_EVNT")
        code.set("codeSystem", "2.16.840.1.113883.5.4")

        # Add narrative (H.1)
        self._add_text_element(investigation, "text", "pv_case.narrative", extractor)

        # Add effective time (report dates)
        self._add_effective_time(investigation, extractor)

        # Add subject1 (patient information)
        self._add_patient_subject(investigation, extractor)

        # Add adverse events
        self._add_adverse_events(investigation, extractor)

        # Add drugs/products
        self._add_products(investigation, extractor)

        # Add diagnostic tests
        self._add_diagnostic_tests(investigation, extractor)

        # Add medical history
        self._add_medical_history(investigation, extractor)

        # Add author (reporter information)
        self._add_author(investigation, extractor)

    def _add_effective_time(self, parent: etree.Element, extractor: DataExtractor):
        """Add effective time for the investigation."""
        effective_time = etree.SubElement(parent, "effectiveTime")

        # Receipt date
        receipt_date = extractor.extract("pv_case.literature.initial_receipt_date")
        if receipt_date:
            low = etree.SubElement(effective_time, "low")
            low.set("value", self._format_date(receipt_date))

    def _add_patient_subject(self, parent: etree.Element, extractor: DataExtractor):
        """Add patient subject with demographics."""
        subject = etree.SubElement(parent, "subject1")
        subject.set("typeCode", "SBJ")

        patient_role = etree.SubElement(subject, "primaryRole")
        patient_role.set("classCode", "PAT")

        # Add patient ID
        patient_id = etree.SubElement(patient_role, "id")
        patient_identifier = extractor.extract("pv_case.patient.identifier") or "UNKNOWN"
        patient_id.set("extension", patient_identifier)
        patient_id.set("root", "2.16.840.1.113883.3.989.2.1.3.5")

        # Add patient entity
        patient = etree.SubElement(patient_role, "subjectOf2")
        patient.set("typeCode", "SBJ")

        observation = etree.SubElement(patient, "observation")
        observation.set("classCode", "OBS")
        observation.set("moodCode", "EVN")

        # Add patient characteristics
        self._add_patient_characteristics(observation, extractor)

    def _add_patient_characteristics(self, parent: etree.Element, extractor: DataExtractor):
        """Add patient characteristics (age, gender, weight, height)."""
        # Gender (D.5)
        gender = extractor.extract("pv_case.patient.gender")
        if gender:
            code = etree.SubElement(parent, "code")
            code.set("code", "C16576")  # Gender code
            code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

            value = etree.SubElement(parent, "value")
            gender_code = "1" if gender and gender.lower() in ["male", "m"] else "2"
            value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "CE")
            value.set("code", gender_code)
            value.set("codeSystem", "2.16.840.1.113883.3.989.2.1.1.20")

        # Age (D.2.2a)
        age = extractor.extract("pv_case.patient.age")
        if age:
            age_obs = etree.SubElement(parent, "component")
            age_value = etree.SubElement(age_obs, "observation")
            age_value.set("classCode", "OBS")
            age_value.set("moodCode", "EVN")

            code = etree.SubElement(age_value, "code")
            code.set("code", "C25150")  # Age code
            code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

            value = etree.SubElement(age_value, "value")
            value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "PQ")
            value.set("value", str(age))

            age_units = extractor.extract("pv_case.patient.age_units") or "a"
            value.set("unit", age_units)

        # Weight (D.3)
        weight = extractor.extract("pv_case.patient.weight")
        if weight:
            weight_obs = etree.SubElement(parent, "component")
            weight_value = etree.SubElement(weight_obs, "observation")
            weight_value.set("classCode", "OBS")
            weight_value.set("moodCode", "EVN")

            code = etree.SubElement(weight_value, "code")
            code.set("code", "C25208")  # Weight code
            code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

            value = etree.SubElement(weight_value, "value")
            value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "PQ")
            value.set("value", str(weight))

            weight_units = extractor.extract("pv_case.patient.weight_units") or "kg"
            value.set("unit", weight_units)

        # Height (D.4)
        height = extractor.extract("pv_case.patient.height")
        if height:
            height_obs = etree.SubElement(parent, "component")
            height_value = etree.SubElement(height_obs, "observation")
            height_value.set("classCode", "OBS")
            height_value.set("moodCode", "EVN")

            code = etree.SubElement(height_value, "code")
            code.set("code", "C25347")  # Height code
            code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

            value = etree.SubElement(height_value, "value")
            value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "PQ")
            value.set("value", str(height))

            height_units = extractor.extract("pv_case.patient.height_units") or "cm"
            value.set("unit", height_units)

    def _add_adverse_events(self, parent: etree.Element, extractor: DataExtractor):
        """Add adverse event information."""
        events = extractor.extract("pv_case.events")
        if not isinstance(events, list):
            return

        for idx, event in enumerate(events):
            if not event.get('is_adverse_event'):
                continue

            component = etree.SubElement(parent, "component")
            adverse_effect = etree.SubElement(component, "adverseEffectObservation")
            adverse_effect.set("classCode", "OBS")
            adverse_effect.set("moodCode", "EVN")

            # Event ID
            event_id = etree.SubElement(adverse_effect, "id")
            event_identifier = event.get("identifier", f"EVT-{idx}")
            event_id.set("extension", event_identifier)
            event_id.set("root", "2.16.840.1.113883.3.989.2.1.3.6")

            # MedDRA code (E.i.2.1b)
            meddra_code = event.get("meddra_code")
            meddra_term = event.get("meddra_term", "")
            if meddra_code:
                code = etree.SubElement(adverse_effect, "code")
                code.set("code", meddra_code)
                code.set("codeSystem", "2.16.840.1.113883.6.163")  # MedDRA
                code.set("displayName", meddra_term)

            # Event description
            if event.get("description"):
                text = etree.SubElement(adverse_effect, "text")
                text.text = event["description"]

            # Start date (E.i.4)
            start_date = event.get("start_date") or event.get("start_date_text")
            if start_date:
                effective_time = etree.SubElement(adverse_effect, "effectiveTime")
                low = etree.SubElement(effective_time, "low")
                low.set("value", self._format_date(start_date))

                # End date (E.i.5)
                end_date = event.get("end_date") or event.get("end_date_text")
                if end_date:
                    high = etree.SubElement(effective_time, "high")
                    high.set("value", self._format_date(end_date))

            # Seriousness (E.i.3.1)
            seriousness = event.get("seriousness_type")
            if seriousness:
                serious_obs = etree.SubElement(adverse_effect, "component")
                serious_val = etree.SubElement(serious_obs, "observation")
                serious_val.set("classCode", "OBS")
                serious_val.set("moodCode", "EVN")

                code = etree.SubElement(serious_val, "code")
                code.set("code", "C48275")  # Seriousness code
                code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

                value = etree.SubElement(serious_val, "value")
                value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "BL")
                value.set("value", "true" if seriousness == "Serious" else "false")

            # Outcome (E.i.7)
            outcome_data = event.get("outcome", {})
            if outcome_data:
                self._add_outcome(adverse_effect, outcome_data)

    def _add_outcome(self, parent: etree.Element, outcome: Dict[str, Any]):
        """Add outcome information for adverse events."""
        outcome_obs = etree.SubElement(parent, "outboundRelationship")
        outcome_obs.set("typeCode", "OUTC")

        observation = etree.SubElement(outcome_obs, "observation")
        observation.set("classCode", "OBS")
        observation.set("moodCode", "EVN")

        # Outcome code
        code = etree.SubElement(observation, "code")
        code.set("code", "C49496")  # Outcome code
        code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

        # Outcome value (E.i.7)
        outcome_name = outcome.get("name", "")
        value = etree.SubElement(observation, "value")
        value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "CE")

        # Map outcome to standard codes
        outcome_map = {
            "recovered": "1",
            "recovering": "2",
            "not recovered": "3",
            "recovered with sequelae": "4",
            "fatal": "5",
            "unknown": "6"
        }
        outcome_code = outcome_map.get(outcome_name.lower(), "6")
        value.set("code", outcome_code)
        value.set("codeSystem", "2.16.840.1.113883.3.989.2.1.1.19")

        # Death information
        if outcome.get("is_death"):
            death_obs = etree.SubElement(observation, "component")
            death_val = etree.SubElement(death_obs, "observation")
            death_val.set("classCode", "OBS")
            death_val.set("moodCode", "EVN")

            code = etree.SubElement(death_val, "code")
            code.set("code", "C48275")
            code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

            # Cause of death
            if outcome.get("cause_of_death"):
                text = etree.SubElement(death_val, "text")
                text.text = outcome["cause_of_death"]

    def _add_products(self, parent: etree.Element, extractor: DataExtractor):
        """Add drug/product information."""
        drugs = extractor.extract("pv_case.drugs")
        if not isinstance(drugs, list):
            return

        for idx, drug in enumerate(drugs):
            component = etree.SubElement(parent, "component")
            product_use = etree.SubElement(component, "substanceAdministration")
            product_use.set("classCode", "SBADM")
            product_use.set("moodCode", "EVN")

            # Drug ID
            drug_id = etree.SubElement(product_use, "id")
            drug_identifier = drug.get("identifier", f"DRG-{idx}")
            drug_id.set("extension", drug_identifier)
            drug_id.set("root", "2.16.840.1.113883.3.989.2.1.3.7")

            # Drug name (G.k.2.2)
            drug_name = drug.get("name")
            if drug_name:
                consumable = etree.SubElement(product_use, "consumable")
                manufactured_product = etree.SubElement(consumable, "manufacturedProduct")
                manufactured_product.set("classCode", "MANU")

                name = etree.SubElement(manufactured_product, "name")
                name.text = drug_name

            # Dosage (G.k.4.r.1a, G.k.4.r.8)
            dosage = drug.get("dosage")
            dosage_units = drug.get("dosage_units")
            if dosage:
                dose_quantity = etree.SubElement(product_use, "doseQuantity")
                dose_quantity.set("value", str(dosage))
                if dosage_units:
                    dose_quantity.set("unit", dosage_units)

            # Route of administration (G.k.4.r.10.1)
            route = drug.get("route_of_administration")
            if route:
                route_code = etree.SubElement(product_use, "routeCode")
                route_code.set("code", self._map_route(route))
                route_code.set("codeSystem", "2.16.840.1.113883.5.112")

            # Start date (G.k.4.r.4)
            start_date = drug.get("start_date") or drug.get("start_date_text")
            if start_date:
                effective_time = etree.SubElement(product_use, "effectiveTime")
                low = etree.SubElement(effective_time, "low")
                low.set("value", self._format_date(start_date))

                # End date
                end_date = drug.get("end_date") or drug.get("end_date_text")
                if end_date:
                    high = etree.SubElement(effective_time, "high")
                    high.set("value", self._format_date(end_date))

            # Drug role (G.k.1)
            role = drug.get("role")
            if role:
                role_obs = etree.SubElement(product_use, "outboundRelationship")
                role_obs.set("typeCode", "PERT")

                observation = etree.SubElement(role_obs, "observation")
                observation.set("classCode", "OBS")
                observation.set("moodCode", "EVN")

                code = etree.SubElement(observation, "code")
                code.set("code", "C53261")  # Drug role code
                code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

                value = etree.SubElement(observation, "value")
                value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "CE")
                role_code = "1" if "suspect" in role.lower() else "2" if "concomitant" in role.lower() else "3"
                value.set("code", role_code)
                value.set("codeSystem", "2.16.840.1.113883.3.989.2.1.1.19")

            # Action taken (G.k.8)
            action = drug.get("action_taken")
            if action:
                action_obs = etree.SubElement(product_use, "outboundRelationship")
                action_obs.set("typeCode", "PERT")

                observation = etree.SubElement(action_obs, "observation")
                observation.set("classCode", "OBS")
                observation.set("moodCode", "EVN")

                code = etree.SubElement(observation, "code")
                code.set("code", "C49647")  # Action taken code
                code.set("codeSystem", "2.16.840.1.113883.3.26.1.1")

                value = etree.SubElement(observation, "value")
                value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "CE")
                value.set("code", self._map_action_taken(action))
                value.set("codeSystem", "2.16.840.1.113883.3.989.2.1.1.17")

    def _add_diagnostic_tests(self, parent: etree.Element, extractor: DataExtractor):
        """Add diagnostic test results."""
        tests = extractor.extract("pv_case.diagnostic_tests")
        if not isinstance(tests, list):
            return

        for idx, test in enumerate(tests):
            component = etree.SubElement(parent, "component")
            test_obs = etree.SubElement(component, "observation")
            test_obs.set("classCode", "OBS")
            test_obs.set("moodCode", "EVN")

            # Test ID
            test_id = etree.SubElement(test_obs, "id")
            test_identifier = test.get("identifier", f"DIA-{idx}")
            test_id.set("extension", test_identifier)
            test_id.set("root", "2.16.840.1.113883.3.989.2.1.3.8")

            # Test code (F.r.2.2b)
            meddra_code = test.get("meddra_code")
            if meddra_code:
                code = etree.SubElement(test_obs, "code")
                code.set("code", meddra_code)
                code.set("codeSystem", "2.16.840.1.113883.6.163")  # MedDRA
                code.set("displayName", test.get("meddra_term", ""))

            # Test result (F.r.3.2)
            test_result = test.get("test_results")
            test_result_text = test.get("test_results_text")
            if test_result or test_result_text:
                value = etree.SubElement(test_obs, "value")

                if test_result:
                    value.set("{http://www.w3.org/2001/XMLSchema-instance}type", "PQ")
                    value.set("value", str(test_result))

                    test_units = test.get("test_units")
                    if test_units:
                        value.set("unit", test_units)

                if test_result_text:
                    text = etree.SubElement(test_obs, "text")
                    text.text = test_result_text

            # Test date (F.r.1)
            test_date = test.get("date_of_test") or test.get("date_of_test_text")
            if test_date:
                effective_time = etree.SubElement(test_obs, "effectiveTime")
                effective_time.set("value", self._format_date(test_date))

    def _add_medical_history(self, parent: etree.Element, extractor: DataExtractor):
        """Add medical history/conditions."""
        conditions = extractor.extract("pv_case.conditions")
        if not isinstance(conditions, list):
            return

        for idx, condition in enumerate(conditions):
            component = etree.SubElement(parent, "component")
            condition_obs = etree.SubElement(component, "observation")
            condition_obs.set("classCode", "OBS")
            condition_obs.set("moodCode", "EVN")

            # Condition ID
            cond_id = etree.SubElement(condition_obs, "id")
            cond_identifier = condition.get("identifier", f"CON-{idx}")
            cond_id.set("extension", cond_identifier)
            cond_id.set("root", "2.16.840.1.113883.3.989.2.1.3.9")

            # Condition code (D.7.1.r.1b)
            meddra_code = condition.get("meddra_code")
            if meddra_code:
                code = etree.SubElement(condition_obs, "code")
                code.set("code", meddra_code)
                code.set("codeSystem", "2.16.840.1.113883.6.163")  # MedDRA
                code.set("displayName", condition.get("meddra_term", ""))

            # Condition comments (D.7.1.r.5)
            comments = condition.get("comments")
            if comments:
                text = etree.SubElement(condition_obs, "text")
                text.text = comments

            # Start date (D.7.1.r.2)
            start_date = condition.get("start_date") or condition.get("start_date_text")
            if start_date:
                effective_time = etree.SubElement(condition_obs, "effectiveTime")
                low = etree.SubElement(effective_time, "low")
                low.set("value", self._format_date(start_date))

                # End date (D.7.1.r.4)
                end_date = condition.get("end_date") or condition.get("end_date_text")
                if end_date:
                    high = etree.SubElement(effective_time, "high")
                    high.set("value", self._format_date(end_date))

    def _add_author(self, parent: etree.Element, extractor: DataExtractor):
        """Add author/reporter information."""
        author_elem = etree.SubElement(parent, "author")
        author_elem.set("typeCode", "AUT")

        # Author role
        assigned_entity = etree.SubElement(author_elem, "assignedEntity")
        assigned_entity.set("classCode", "ASSIGNED")

        # Author ID
        author_id = etree.SubElement(assigned_entity, "id")
        author_identifier = extractor.extract("pv_case.literature.author.identifier") or "UNKNOWN"
        author_id.set("extension", author_identifier)
        author_id.set("root", "2.16.840.1.113883.3.989.2.1.3.10")

        # Author name
        author_name = extractor.extract("pv_case.literature.author.name")
        if author_name:
            assigned_person = etree.SubElement(assigned_entity, "assignedPerson")
            assigned_person.set("classCode", "PSN")

            name = etree.SubElement(assigned_person, "name")
            name.text = author_name

        # Organization
        org_title = extractor.extract("pv_case.literature.author.author_organizations[0].organization.title")
        if org_title:
            represented_org = etree.SubElement(assigned_entity, "representedOrganization")
            represented_org.set("classCode", "ORG")

            org_name = etree.SubElement(represented_org, "name")
            org_name.text = org_title

            # Department
            org_dept = extractor.extract("pv_case.literature.author.author_organizations[0].organization.department")
            if org_dept:
                part_of = etree.SubElement(represented_org, "asOrganizationPartOf")
                whole_org = etree.SubElement(part_of, "wholeOrganization")
                whole_org.set("classCode", "ORG")

                dept_name = etree.SubElement(whole_org, "name")
                dept_name.text = org_dept

    def _add_text_element(self, parent: etree.Element, tag_name: str, json_path: str, extractor: DataExtractor):
        """Add a text element from JSON data."""
        value = extractor.extract(json_path)
        if value:
            elem = etree.SubElement(parent, tag_name)
            elem.text = str(value)

    def _format_date(self, date_value: Any) -> str:
        """
        Format a date value to HL7 format (YYYYMMDD or YYYYMMDDHHMMSS).

        Args:
            date_value: Date value (string or datetime object)

        Returns:
            Formatted date string
        """
        if not date_value:
            return ""

        # If it's already in text format, return as is
        if isinstance(date_value, str):
            # Try to extract a date from text
            import re
            # Remove common date patterns
            cleaned = re.sub(r'[^\d]', '', date_value[:20])
            if len(cleaned) >= 8:
                return cleaned[:8]
            return cleaned

        # If it's a datetime object
        if hasattr(date_value, 'strftime'):
            return date_value.strftime("%Y%m%d")

        return str(date_value)

    def _map_route(self, route: str) -> str:
        """Map route of administration to standard code."""
        route_map = {
            "oral": "PO",
            "intravenous": "IV",
            "intramuscular": "IM",
            "subcutaneous": "SC",
            "topical": "TOP",
            "rectal": "PR",
        }
        return route_map.get(route.lower(), "OTH")

    def _map_action_taken(self, action: str) -> str:
        """Map action taken to standard code."""
        action_map = {
            "permanently discontinued": "1",
            "dose reduced": "2",
            "dose increased": "3",
            "dose not changed": "4",
            "unknown": "5",
            "not applicable": "6",
        }
        return action_map.get(action.lower(), "5")

    def to_string(self, root: etree.Element, pretty_print: bool = True) -> str:
        """
        Convert XML element to string.

        Args:
            root: The root XML element
            pretty_print: Whether to format with indentation

        Returns:
            XML string
        """
        return etree.tostring(
            root,
            pretty_print=pretty_print,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')

    def save_to_file(self, root: etree.Element, output_path: str, pretty_print: bool = True):
        """
        Save XML to file.

        Args:
            root: The root XML element
            output_path: Path to save the XML file
            pretty_print: Whether to format with indentation
        """
        xml_string = self.to_string(root, pretty_print)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
