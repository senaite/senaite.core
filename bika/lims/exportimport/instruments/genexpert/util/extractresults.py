class ExtractResults(object):

    @staticmethod
    def is_message_result(msg):

        is_result = False
        print msg.msh.msh_9
        if (str(msg.msh.msh_9.value) == 'ORU^R32^ORU_R30'):
            is_result = True

        return is_result

    @staticmethod
    def is_intented_receipient(msg):

        intended_receipient = False
        if (msg.msh.msh_5.value == 'BIKALIS'):
            intended_receipient = True

        return intended_receipient

    @staticmethod
    def get_specimen_id(msg):

        return msg.spm.spm_2.value

    @staticmethod
    def get_patient_id(msg):

        return msg.pid.pid_1.value

    @staticmethod
    def get_assay_code(msg):

        return msg.ORU_R30_OBSERVATION.obx.obx_3.value.split('&', 3 )[2]

    @staticmethod
    def get_speciment_role(msg):

        if msg.spm.spm_11.value == 'Q':
            return 'quality_control_specimen'
        else:
            return 'patient_specimen'

    @staticmethod
    def get_results_values(msg):

        genexpert_result = {}
        for x in msg.ORU_R30_OBSERVATION:
            if x.obx.obx_5.obx_5_2.value:
                genexpert_result[x.obx.obx_4.value] = x.obx.obx_5.obx_5_2.value
            elif x.obx.obx_5.obx_5_1.value:
                genexpert_result[x.obx.obx_4.value] = x.obx.obx_5.obx_5_1.value

        return genexpert_result

    @staticmethod
    def get_result(genexpert_result_dict):

        result = ''

        if genexpert_result_dict['Ebola GP'] == 'DETECTED' and genexpert_result_dict['Ebola NP'] == 'NOT DETECTED':
            result = '1'
        elif genexpert_result_dict['Ebola GP'] == 'NOT DETECTED' and genexpert_result_dict['Ebola NP'] == 'DETECTED':
            result = '1'
        elif genexpert_result_dict['Ebola GP'] == 'DETECTED' and genexpert_result_dict['Ebola NP'] == 'DETECTED':
            result = '3'
        elif genexpert_result_dict['Ebola GP'] == 'NOT DETECTED' and genexpert_result_dict['Ebola NP'] == 'NOT DETECTED':
            result = '2'

        return result

    @staticmethod
    def make_checksum(message):

        if not isinstance(message[0], int):
            message = map(ord, message)

        return hex(sum(message) & 0xFF)[2:].upper().zfill(2).encode()

    @staticmethod
    def loadresultarray(hl7message):

        lisresult = ExtractResults.get_results_values(hl7message)
        assay_result = ExtractResults.get_result(lisresult)
        lisresult['result'] = assay_result
        lisresult['specimen_id'] = ExtractResults.get_specimen_id(hl7message)
        lisresult['patient_id'] = ExtractResults.get_patient_id(hl7message)
        lisresult['assay_code'] = ExtractResults.get_assay_code(hl7message)

        return lisresult
