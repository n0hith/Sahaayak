import type { DocumentId, Scheme } from '../types'

export const documentLabels: Record<DocumentId, string> = {
  identity: 'Identity proof (example)',
  address: 'Address proof (example)',
  income: 'Income certificate (example)',
  education: 'Education record (example)',
  land: 'Land record (example)',
  bank: 'Bank account proof (example)',
  enrollment: 'Current enrolment document (example)',
  referral: 'Health-support referral card (example)',
  businessPlan: 'Simple business plan (example)',
}

export const schemes: Scheme[] = [
  {
    id: 'nayi-disha', name: 'Nayi Disha Scholarship Support', icon: '✦', category: 'Education',
    summary: 'Mock learning-cost support for students continuing higher education.',
    whoItMayHelp: 'Students aged 17–25 in a lower-income household who are enrolled in higher education.',
    support: 'Estimated demo support: up to ₹18,000 per academic year',
    rules: [
      { field: 'age', operator: 'ageBetween', value: '17-25', label: 'Age 17–25' },
      { field: 'incomeBand', operator: 'incomeAtMost', value: '15to3', label: 'Household income up to ₹3 lakh/year' },
      { field: 'situations', operator: 'includes', value: 'student', label: 'Currently a student' },
      { field: 'educationStage', operator: 'equals', value: 'higher', label: 'Higher education stage' },
      { field: 'enrolled', operator: 'equals', value: 'yes', label: 'Currently enrolled' },
    ],
    requiredDocuments: ['identity', 'income', 'education', 'enrollment'], preparationTime: 'About 2–5 days',
    nextSteps: ['Gather your education and income documents.', 'Confirm the latest terms with the official provider.', 'Apply through the relevant official channel.', 'Save any acknowledgement or reference number.'],
    availability: 'Demo availability: applications simulated', privacyNote: 'Only share documents with the official provider after you have verified the channel.'
  },
  {
    id: 'swasthya-saathi', name: 'Swasthya Saathi Family Care', icon: '✚', category: 'Health',
    summary: 'Mock referral-led health-support guidance for lower-income households.',
    whoItMayHelp: 'Lower-income households that need a health-support referral card.',
    support: 'Estimated demo support: referral for a care-support package',
    rules: [
      { field: 'incomeBand', operator: 'incomeAtMost', value: '15to3', label: 'Household income up to ₹3 lakh/year' },
    ],
    requiredDocuments: ['identity', 'address', 'income', 'referral'], optionalDocuments: ['bank'], preparationTime: 'About 3–7 days',
    nextSteps: ['Gather the documents you have.', 'Ask the official provider about referral-card eligibility.', 'Use the official channel if eligible.', 'Keep the official acknowledgement safely.'],
    availability: 'Demo availability: provider confirmation needed', privacyNote: 'Do not describe medical details in Sahaayak; discuss them only with an appropriate official provider.'
  },
  {
    id: 'kisan-sahayog', name: 'Kisan Sahayog Input Grant', icon: '♧', category: 'Farming',
    summary: 'Mock seasonal input-cost support for small and marginal farming households.',
    whoItMayHelp: 'Farming households with a small or marginal landholding.',
    support: 'Estimated demo support: ₹6,000 seasonal input grant',
    rules: [
      { field: 'situations', operator: 'includes', value: 'farmer', label: 'Farming household' },
      { field: 'landholding', operator: 'oneOf', value: ['marginal', 'small'], label: 'Small or marginal landholding' },
    ],
    requiredDocuments: ['identity', 'land', 'bank'], preparationTime: 'About 2–4 days',
    nextSteps: ['Gather land and bank proof.', 'Confirm the current local requirements.', 'Submit only through the official channel.', 'Save the acknowledgement number.'],
    availability: 'Demo availability: seasonal example', privacyNote: 'Sahaayak never checks land records or account details.'
  },
  {
    id: 'udyam-shuru', name: 'Udyam Shuru Microbusiness Support', icon: '↗', category: 'Work',
    summary: 'Mock start-up guidance and small-support pathway for new local businesses.',
    whoItMayHelp: 'Adults planning a small business in a household below the demo income threshold.',
    support: 'Estimated demo support: up to ₹25,000 plus local mentoring',
    rules: [
      { field: 'age', operator: 'ageBetween', value: '18-65', label: 'Age 18 or above' },
      { field: 'incomeBand', operator: 'incomeAtMost', value: '3to5', label: 'Household income up to ₹5 lakh/year' },
      { field: 'planningBusiness', operator: 'equals', value: 'yes', label: 'Planning a small business' },
    ],
    requiredDocuments: ['identity', 'address', 'income', 'businessPlan'], optionalDocuments: ['bank'], preparationTime: 'About 5–10 days',
    nextSteps: ['Write a one-page business idea.', 'Confirm eligibility with the official provider.', 'Use the official channel to submit.', 'Save the acknowledgement/reference number.'],
    availability: 'Demo availability: orientation example', privacyNote: 'Do not enter sales, account, or business registration details here.'
  },
  {
    id: 'ghar-urja', name: 'Ghar Urja Clean-Cooking Support', icon: '◒', category: 'Home',
    summary: 'Mock support pathway for households without a current clean-cooking connection.',
    whoItMayHelp: 'Lower-income households that do not currently have a clean-cooking connection.',
    support: 'Estimated demo support: connection-fee assistance and safety orientation',
    rules: [
      { field: 'incomeBand', operator: 'incomeAtMost', value: '15to3', label: 'Household income up to ₹3 lakh/year' },
      { field: 'cleanCooking', operator: 'equals', value: 'no', label: 'No current clean-cooking connection' },
    ],
    requiredDocuments: ['identity', 'address', 'income'], preparationTime: 'About 2–6 days',
    nextSteps: ['Check whether your household already has a connection.', 'Confirm requirements with the official provider.', 'Apply using the official channel if appropriate.', 'Keep the acknowledgement/reference number.'],
    availability: 'Demo availability: connection status must be confirmed', privacyNote: 'Sahaayak does not collect utility account numbers or visit your address.'
  },
  {
    id: 'kaushal-nayi-raah', name: 'Kaushal Nayi Raah Training Voucher', icon: '◎', category: 'Skills',
    summary: 'Mock vocational-training voucher for people preparing for work or a career change.',
    whoItMayHelp: 'Jobseekers, workers, and students aged 18–35 seeking skills training.',
    support: 'Estimated demo support: training-fee voucher up to ₹12,000',
    rules: [
      { field: 'age', operator: 'ageBetween', value: '18-35', label: 'Age 18–35' },
      { field: 'situations', operator: 'oneOf', value: ['jobseeker', 'employed', 'student'], label: 'Seeking work, studying, or working' },
    ],
    requiredDocuments: ['identity'], optionalDocuments: ['education', 'address'], preparationTime: 'About 1–3 days',
    nextSteps: ['Choose a training area.', 'Check the course and provider criteria.', 'Apply through the official channel.', 'Save your acknowledgement/reference number.'],
    availability: 'Demo availability: course list is fictional', privacyNote: 'Choose a training provider only after independently confirming its credentials.'
  },
]
