import { FhirResource, NormalizedRecord } from '../types/index.js';

export class NormalizerService {
    normalize(resource: FhirResource): NormalizedRecord | null {
        const { resourceType, id } = resource;
        let textContent = '';
        let clinicalDate = '1970-01-01';
        let patientId = '';
        let patientName = '';
        let category = '';
        let tags: string[] = [];

        // Extract common fields
        if (resource.subject?.reference?.startsWith('Patient/')) {
            patientId = resource.subject.reference.split('/')[1];
        } else if (resource.patient?.reference?.startsWith('Patient/')) {
            patientId = resource.patient.reference.split('/')[1];
        } else if (resourceType === 'Patient') {
            patientId = id;
            patientName = this.formatName(resource.name);
        }

        switch (resourceType) {
            case 'Patient':
                textContent = `Patient: ${patientName}. Gender: ${resource.gender}. Birth Date: ${resource.birthDate}.`;
                clinicalDate = resource.birthDate || clinicalDate;
                tags.push('patient');
                break;

            case 'Observation':
                const obsCode = resource.code?.coding?.[0]?.display || resource.code?.text || 'Unknown Observation';
                const value = resource.valueQuantity ? `${resource.valueQuantity.value} ${resource.valueQuantity.unit}` : resource.valueString || '';
                clinicalDate = resource.effectiveDateTime || resource.issued || clinicalDate;
                category = resource.category?.[0]?.coding?.[0]?.display || '';
                textContent = `Observation: ${obsCode}. Value: ${value}. Date: ${clinicalDate}.`;
                if (category.toLowerCase().includes('vital')) tags.push('vitals');
                if (category.toLowerCase().includes('lab')) tags.push('lab');
                tags.push('observation');
                break;

            case 'Condition':
                const condName = resource.code?.coding?.[0]?.display || resource.code?.text || 'Unknown Condition';
                clinicalDate = resource.onsetDateTime || resource.recordedDate || clinicalDate;
                const status = resource.clinicalStatus?.coding?.[0]?.code || '';
                textContent = `Condition: ${condName}. Status: ${status}. Onset: ${clinicalDate}.`;
                tags.push('diagnosis', 'condition');
                break;

            case 'AllergyIntolerance':
                const allergyName = resource.code?.coding?.[0]?.display || resource.code?.text || 'Unknown Allergy';
                clinicalDate = resource.recordedDate || clinicalDate;
                const criticality = resource.criticality || 'unknown';
                textContent = `Allergy: ${allergyName}. Criticality: ${criticality}. Recorded: ${clinicalDate}.`;
                tags.push('allergy');
                break;

            case 'MedicationRequest':
                const medName = resource.medicationCodeableConcept?.coding?.[0]?.display || resource.medicationCodeableConcept?.text || 'Unknown Medication';
                clinicalDate = resource.authoredOn || clinicalDate;
                const dose = resource.dosageInstruction?.[0]?.text || '';
                textContent = `Medication: ${medName}. Dosage: ${dose}. Status: ${resource.status}. Authored: ${clinicalDate}.`;
                tags.push('medication');
                break;

            case 'Procedure':
                const procName = resource.code?.coding?.[0]?.display || resource.code?.text || 'Unknown Procedure';
                clinicalDate = resource.performedDateTime || clinicalDate;
                textContent = `Procedure: ${procName}. Date: ${clinicalDate}. Status: ${resource.status}.`;
                tags.push('procedure');
                break;

            case 'Encounter':
                const encType = resource.type?.[0]?.coding?.[0]?.display || 'Unknown Encounter';
                clinicalDate = resource.period?.start || clinicalDate;
                textContent = `Encounter: ${encType}. Date: ${clinicalDate}. Status: ${resource.status}. Reason: ${resource.reasonCode?.[0]?.text || 'N/A'}`;
                tags.push('encounter');
                break;

            case 'Immunization':
                const vaccine = resource.vaccineCode?.coding?.[0]?.display || 'Unknown Vaccine';
                clinicalDate = resource.occurrenceDateTime || clinicalDate;
                textContent = `Immunization: ${vaccine}. Date: ${clinicalDate}. Status: ${resource.status}.`;
                tags.push('immunization');
                break;

            case 'DiagnosticReport':
                const reportName = resource.code?.coding?.[0]?.display || 'Unknown Report';
                clinicalDate = resource.effectiveDateTime || resource.issued || clinicalDate;
                textContent = `Diagnostic Report: ${reportName}. Date: ${clinicalDate}. Result count: ${resource.result?.length || 0}.`;
                tags.push('diagnostic-report');
                break;

            default:
                return null;
        }

        return {
            id: `${resourceType}-${id}`,
            patientId,
            patientName,
            resourceType,
            resourceId: id,
            clinicalDate,
            category,
            status: resource.status || (resource.clinicalStatus?.coding?.[0]?.code),
            textContent,
            metadata: {
                originalResource: JSON.stringify(resource),
                tags,
                codeText: resource.code?.text,
                display: resource.code?.coding?.[0]?.display
            }
        };
    }

    private formatName(name: any[]): string {
        if (!name || name.length === 0) return 'Unknown';
        const first = name[0];
        const given = first.given ? first.given.join(' ') : '';
        const family = first.family || '';
        return `${given} ${family}`.trim();
    }
}
