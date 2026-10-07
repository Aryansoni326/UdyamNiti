/**
 * UdyamNiti - Multi-language Translation Dictionary
 * Supports: English (en), Hindi (hi), Gujarati (gu)
 */

export type Language = 'en' | 'hi' | 'gu'

export const LANGUAGE_LABELS: Record<Language, string> = {
  en: 'English',
  hi: 'हिन्दी',
  gu: 'ગુજરાતી',
}

export const translations = {
  // ─── APPSHELL / HEADER ──────────────────────────────────────────────────────
  appName: {
    en: 'UdyamNiti',
    hi: 'उद्यमनीति',
    gu: 'ઉદ્યમનીતિ',
  },
  tagline: {
    en: 'National MSME Scheme Gateway',
    hi: 'राष्ट्रीय MSME योजना पोर्टल',
    gu: 'રાષ્ટ્રીય MSME યોજના પોર્ટલ',
  },
  signIn: {
    en: 'Sign In',
    hi: 'साइन इन',
    gu: 'સાઇન ઇન',
  },
  register: {
    en: 'Register',
    hi: 'रजिस्टर',
    gu: 'રજીસ્ટર',
  },
  dashboard: {
    en: 'Dashboard',
    hi: 'डैशबोर्ड',
    gu: 'ડેશબોર્ડ',
  },
  signOut: {
    en: 'Sign Out',
    hi: 'साइन आउट',
    gu: 'સાઇન આઉટ',
  },
  loggedInAs: {
    en: 'Logged in as',
    hi: 'के रूप में लॉग इन',
    gu: 'તરીકે લૉગ ઇન',
  },
  schemesDashboard: {
    en: 'Schemes Dashboard',
    hi: 'योजना डैशबोर्ड',
    gu: 'યોજના ડેશબોર્ડ',
  },

  // ─── NAVBAR ──────────────────────────────────────────────────────────────────
  home: {
    en: 'Home',
    hi: 'होम',
    gu: 'હોમ',
  },
  ministry: {
    en: 'Ministry',
    hi: 'मंत्रालय',
    gu: 'મંત્રાલય',
  },
  schemesAndBenefits: {
    en: 'Schemes & Benefits',
    hi: 'योजनाएं और लाभ',
    gu: 'યોજનાઓ અને લાભો',
  },
  resources: {
    en: 'Resources',
    hi: 'संसाधन',
    gu: 'સંસાધનો',
  },
  updates: {
    en: 'Updates',
    hi: 'अपडेट्स',
    gu: 'અપડેટ્સ',
  },
  support: {
    en: 'Support',
    hi: 'सहायता',
    gu: 'સહાયતા',
  },
  findBenefitsForMyBusiness: {
    en: '✨ Find Benefits for My Business',
    hi: '✨ मेरे व्यवसाय के लिए लाभ खोजें',
    gu: '✨ મારા વ્યવસાય માટે લાભો શોધો',
  },
  searchPlaceholder: {
    en: 'Search schemes, benefits or programs...',
    hi: 'योजनाएं, लाभ या कार्यक्रम खोजें...',
    gu: 'યોજનાઓ, લાભો અથવા કાર્યક્રમો શોધો...',
  },

  // ─── MINISTRY DROPDOWN ──────────────────────────────────────────────────────
  aboutMinistry: {
    en: 'About the Ministry',
    hi: 'मंत्रालय के बारे में',
    gu: 'મંત્રાલય વિશે',
  },
  aboutMinistryDesc: {
    en: 'History, Role & Objectives of M/o MSME',
    hi: 'MSME मंत्रालय का इतिहास, भूमिका और उद्देश्य',
    gu: 'MSME મંત્રાલયનો ઇતિહાસ, ભૂમિકા અને ઉદ્દેશ્યો',
  },
  visionMission: {
    en: 'Vision, Mission & Objectives',
    hi: 'विजन, मिशन और उद्देश्य',
    gu: 'વિઝન, મિશન અને ઉદ્દેશ્યો',
  },
  visionMissionDesc: {
    en: 'Empowering competitive & sustainable MSMEs',
    hi: 'प्रतिस्पर्धी और टिकाऊ MSMEs को सशक्त बनाना',
    gu: 'સ્પર્ધાત્મક અને ટકાઉ MSMEs ને સશક્ત બનાવવું',
  },
  leadership: {
    en: 'Leadership',
    hi: 'नेतृत्व',
    gu: 'નેતૃત્વ',
  },
  leadershipDesc: {
    en: 'Hon’ble Ministers & Administrative Leadership',
    hi: 'माननीय मंत्री और प्रशासनिक नेतृत्व',
    gu: 'માનનીય મંત્રીઓ અને વહીવટી નેતૃત્વ',
  },
  divisions: {
    en: 'Divisions',
    hi: 'प्रभाग',
    gu: 'વિભાગો',
  },
  divisionsDesc: {
    en: 'Policy, Credit, Technology, SME & ARI',
    hi: 'नीति, ऋण, प्रौद्योगिकी, SME और ARI प्रभाग',
    gu: 'નીતિ, ક્રેડિટ, ટેકનોલોજી, SME અને ARI વિભાગો',
  },
  organisations: {
    en: 'Organisations',
    hi: 'संगठन',
    gu: 'સંસ્થાઓ',
  },
  organisationsDesc: {
    en: 'DC-MSME, NSIC, KVIC, Coir Board, NI-MSME, MGIRI',
    hi: 'DC-MSME, NSIC, KVIC, कॉयर बोर्ड, NI-MSME, MGIRI',
    gu: 'DC-MSME, NSIC, KVIC, કોઈર બોર્ડ, NI-MSME, MGIRI',
  },
  rolesAndResponsibilities: {
    en: 'Roles & Responsibilities',
    hi: 'भूमिकाएं और जिम्मेदारियां',
    gu: 'ભૂમિકાઓ અને જવાબદારીઓ',
  },
  rolesAndResponsibilitiesDesc: {
    en: 'Finance, Tech, Skills, Infra, Marketing & Quality',
    hi: 'वित्त, प्रौद्योगिकी, कौशल, बुनियादी ढांचा, विपणन और गुणवत्ता',
    gu: 'નાણા, ટેકનોલોજી, કૌશલ્ય, ઈન્ફ્રા, માર્કેટિંગ અને ગુણવત્તા',
  },
  msmeOverview: {
    en: 'MSME Overview',
    hi: 'MSME अवलोकन',
    gu: 'MSME ઝાંખી',
  },
  msmeOverviewDesc: {
    en: 'Classification criteria & Udyam Registration',
    hi: 'वर्गीकरण मानदंड और उद्यम पंजीकरण',
    gu: 'વર્ગીકરણ માપદંડ અને ઉદ્યમ નોંધણી',
  },
  ministryDirectory: {
    en: 'Ministry Directory',
    hi: 'मंत्रालय निर्देशिका',
    gu: 'મંત્રાલય ડિરેક્ટરી',
  },
  ministryDirectoryDesc: {
    en: 'Search officers, nodal desks & phone numbers',
    hi: 'अधिकारियों, नोडल डेस्क और फोन नंबर खोजें',
    gu: 'અધિકારીઓ, નોડલ ડેસ્ક અને ફોન નંબર શોધો',
  },

  // ─── SCHEMES & BENEFITS DROPDOWN ────────────────────────────────────────────
  exploreAllSchemes: {
    en: 'Explore All Schemes',
    hi: 'सभी योजनाएं देखें',
    gu: 'બધી યોજનાઓ જુઓ',
  },
  findSchemesForMyBusiness: {
    en: 'Find Schemes for My Business ⭐',
    hi: 'मेरे व्यवसाय के लिए योजनाएं खोजें ⭐',
    gu: 'મારા વ્યવસાય માટે યોજનાઓ શોધો ⭐',
  },
  creditAndFinance: {
    en: 'Credit & Finance',
    hi: 'ऋण और वित्त',
    gu: 'ક્રેડિટ અને નાણાં',
  },
  subsidiesAndIncentives: {
    en: 'Subsidies & Incentives',
    hi: 'सब्सिडी और प्रोत्साहन',
    gu: 'સબસિડી અને પ્રોત્સાહનો',
  },
  technologyAndInnovation: {
    en: 'Technology & Innovation',
    hi: 'प्रौद्योगिकी और नवाचार',
    gu: 'ટેકનોલોજી અને નવીનતા',
  },
  skillDevelopment: {
    en: 'Skill Development',
    hi: 'कौशल विकास',
    gu: 'કૌશલ્ય વિકાસ',
  },
  marketingSupport: {
    en: 'Marketing Support',
    hi: 'विपणन सहायता',
    gu: 'માર્કેટિંગ સપોર્ટ',
  },
  exportSupport: {
    en: 'Export Support',
    hi: 'निर्यात सहायता',
    gu: 'નિકાસ સહાય',
  },
  infrastructureAndClusters: {
    en: 'Infrastructure & Clusters',
    hi: 'बुनियादी ढांचा और क्लस्टर',
    gu: 'ઇન્ફ્રાસ્ટ્રક્ચર અને ક્લસ્ટર્સ',
  },
  womenEntrepreneurs: {
    en: 'Women Entrepreneurs',
    hi: 'महिला उद्यमी',
    gu: 'મહિલા ઉદ્યોગસાહસિકો',
  },
  scstEntrepreneurs: {
    en: 'SC/ST Entrepreneurs',
    hi: 'एससी/एसटी उद्यमी',
    gu: 'SC/ST ઉદ્યોગસાહસિકો',
  },
  startupAndEntrepreneurship: {
    en: 'Startup & Entrepreneurship',
    hi: 'स्टार्टअप और उद्यमिता',
    gu: 'સ્ટાર્ટઅપ અને સાહસિકતા',
  },

  // ─── RESOURCES DROPDOWN ─────────────────────────────────────────────────────
  actsAndRules: {
    en: 'Acts & Rules',
    hi: 'अधिनियम और नियम',
    gu: 'કાયદા અને નિયમો',
  },
  policies: {
    en: 'Policies',
    hi: 'नीतियां',
    gu: 'નીતિઓ',
  },
  schemeGuidelines: {
    en: 'Scheme Guidelines (Official PDFs)',
    hi: 'योजना दिशानिर्देश (आधिकारिक PDF)',
    gu: 'યોજના માર્ગદર્શિકા (અધિકૃત PDF)',
  },
  notifications: {
    en: 'Notifications',
    hi: 'अधिसूचनाएं',
    gu: 'સૂચનાઓ',
  },
  circularsAndOrders: {
    en: 'Circulars & Orders',
    hi: 'परिपत्र और आदेश',
    gu: 'પરિપત્રો અને ઓર્ડર',
  },
  reports: {
    en: 'Reports',
    hi: 'रिपोर्ट्स',
    gu: 'અહેવાલો',
  },
  publications: {
    en: 'Publications',
    hi: 'प्रकाशन',
    gu: 'પ્રકાશનો',
  },
  formsAndTemplates: {
    en: 'Forms & Templates',
    hi: 'प्रपत्र और टेम्पलेट',
    gu: 'ફોર્મ્સ અને નમૂનાઓ',
  },

  // ─── UPDATES DROPDOWN ───────────────────────────────────────────────────────
  whatsNew: {
    en: "What's New",
    hi: 'क्या नया है',
    gu: 'શું નવું છે',
  },
  announcements: {
    en: 'Announcements',
    hi: 'घोषणाएं',
    gu: 'ઘોષણાઓ',
  },
  schemeUpdates: {
    en: 'Scheme Updates',
    hi: 'योजना अपडेट',
    gu: 'યોજના અપડેટ્સ',
  },
  events: {
    en: 'Events',
    hi: 'कार्यक्रम',
    gu: 'ઇવેન્ટ્સ',
  },
  pressReleases: {
    en: 'Press Releases',
    hi: 'प्रेस विज्ञप्तियां',
    gu: 'પ્રેસ રિલીઝ',
  },
  successStories: {
    en: 'Success Stories',
    hi: 'सफलता की कहानियां',
    gu: 'સફળતાની વાર્તાઓ',
  },
  photoGallery: {
    en: 'Photo Gallery',
    hi: 'फोटो गैलरी',
    gu: 'ફોટો ગેલેરી',
  },
  videoGallery: {
    en: 'Video Gallery',
    hi: 'वीडियो गैलरी',
    gu: 'વીડિયો ગેલેરી',
  },

  // ─── SUPPORT DROPDOWN ───────────────────────────────────────────────────────
  helpCentre: {
    en: 'Help Centre',
    hi: 'सहायता केंद्र',
    gu: 'સહાય કેન્દ્ર',
  },
  contactMinistry: {
    en: 'Contact Ministry',
    hi: 'मंत्रालय से संपर्क करें',
    gu: 'મંત્રાલયનો સંપર્ક કરો',
  },
  grievanceSupport: {
    en: 'Grievance Support (Champions Portal)',
    hi: 'शिकायत निवारण (चैंपियंस पोर्टल)',
    gu: 'ફરિયાદ નિવારણ (ચેમ્પિયન્સ પોર્ટલ)',
  },
  applicationHelp: {
    en: 'Application Help',
    hi: 'आवेदन सहायता',
    gu: 'અરજી સહાય',
  },
  askAiAssistant: {
    en: 'Ask MSME AI Assistant',
    hi: 'MSME AI सहायक से पूछें',
    gu: 'MSME AI સહાયકને પૂછો',
  },

  close: {
    en: 'Close',
    hi: 'बंद करें',
    gu: 'બંધ કરો',
  },

  // ─── LANDING PAGE - SLIDES ──────────────────────────────────────────────────
  slide1Tag: {
    en: 'National MSME Initiative',
    hi: 'राष्ट्रीय MSME पहल',
    gu: 'રાષ્ટ્રીય MSME પહેલ',
  },
  slide1Title: {
    en: 'Share your ideas & Suggestions with PM for MSME Growth',
    hi: 'MSME विकास के लिए प्रधानमंत्री को अपने विचार और सुझाव साझा करें',
    gu: 'MSME વિકાસ માટે PM ને તમારા વિચારો અને સૂચનો શેર કરો',
  },
  slide1Highlight: {
    en: 'Mann Ki Baat on 27th September, 2026',
    hi: 'मन की बात 27 सितंबर, 2026',
    gu: 'મન કી બાત 27 સપ્ટેમ્બર, 2026',
  },
  slide1Subtitle: {
    en: 'Click Here or Dial 1800 11 7800 (Toll-Free) - Phone lines open for Indian MSME Entrepreneurs',
    hi: 'यहां क्लिक करें या डायल करें 1800 11 7800 (टोल-फ्री) - भारतीय MSME उद्यमियों के लिए फोन लाइन खुली',
    gu: 'અહીં ક્લિક કરો અથવા 1800 11 7800 ડાયલ કરો (ટોલ-ફ્રી) - ભારતીય MSME ઉદ્યમીઓ માટે ફોન લાઇન ખુલ્લી',
  },
  slide1Cta: {
    en: 'Explore Central Schemes',
    hi: 'केंद्रीय योजनाएं देखें',
    gu: 'કેન્દ્રીય યોજનાઓ જુઓ',
  },
  slide2Tag: {
    en: 'Quality & Zero Defect Manufacturing',
    hi: 'गुणवत्ता और शून्य दोष विनिर्माण',
    gu: 'ગુણવત્તા અને ઝીરો ડિફેક્ટ ઉત્પાદન',
  },
  slide2Title: {
    en: 'MSME Sustainable (ZED) Certification Scheme Phase-II',
    hi: 'MSME सतत (ZED) प्रमाणन योजना चरण-II',
    gu: 'MSME ટકાઉ (ZED) પ્રમાણન યોજના ફેઝ-II',
  },
  slide2Highlight: {
    en: 'Up to 80% Subsidy on Certification & Audits',
    hi: 'प्रमाणन और ऑडिट पर 80% तक सब्सिडी',
    gu: 'પ્રમાણન અને ઓડિટ પર 80% સુધી સબસિડી',
  },
  slide2Subtitle: {
    en: 'Attain Bronze, Silver, and Gold quality certifications to export globally with complete reimbursement on technology assessment.',
    hi: 'प्रौद्योगिकी मूल्यांकन पर पूर्ण प्रतिपूर्ति के साथ विश्व स्तर पर निर्यात के लिए ब्रॉन्ज, सिल्वर और गोल्ड गुणवत्ता प्रमाणन प्राप्त करें।',
    gu: 'ટેક્નોલોજી મૂલ્યાંકન પર સંપૂર્ણ ભરપાઈ સાથે વૈશ્વિક નિકાસ માટે બ્રોન્ઝ, સિલ્વર અને ગોલ્ડ ગુણવત્તા પ્રમાણન મેળવો.',
  },
  slide2Cta: {
    en: 'Claim ZED Subsidy',
    hi: 'ZED सब्सिडी का दावा करें',
    gu: 'ZED સબસિડી ક્લેમ કરો',
  },
  registerEnterprise: {
    en: 'Register Enterprise',
    hi: 'उद्यम रजिस्टर करें',
    gu: 'ઉદ્યમ રજીસ્ટર કરો',
  },
  officialInitiative: {
    en: 'Official Initiative - Ministry of MSME, Govt of India',
    hi: 'आधिकारिक पहल - MSME मंत्रालय, भारत सरकार',
    gu: 'અધિકૃત પહેલ - MSME મંત્રાલય, ભારત સરકાર',
  },

  // ─── ANNOUNCEMENTS ──────────────────────────────────────────────────────────
  announcements: {
    en: 'Announcements',
    hi: 'घोषणाएं',
    gu: 'જાહેરાતો',
  },
  announcement1: {
    en: '⚠️ Beware of Fake Sites. For MSME Udyam Registration, visit only official portal udyamregistration.gov.in',
    hi: '⚠️ नकली साइटों से सावधान रहें। MSME उद्यम पंजीकरण के लिए, केवल आधिकारिक पोर्टल udyamregistration.gov.in पर जाएं',
    gu: '⚠️ બનાવટી સાઇટ્સથી સાવધ રહો. MSME ઉદ્યમ નોંધણી માટે, ફક્ત અધિકૃત પોર્ટલ udyamregistration.gov.in પર જાઓ',
  },
  announcement2: {
    en: '📄 New Operational Guidelines issued for SFURTI and PM-EGP Capital Subsidy Schemes 2025-26',
    hi: '📄 SFURTI और PM-EGP पूंजी सब्सिडी योजनाओं 2025-26 के लिए नए परिचालन दिशानिर्देश जारी',
    gu: '📄 SFURTI અને PM-EGP મૂડી સબસિડી યોજનાઓ 2025-26 માટે નવી ઓપરેશનલ માર્ગદર્શિકાઓ જારી',
  },
  announcement3: {
    en: '🏛️ TReDS Circular 262 - Enhanced invoice discounting limits for Micro and Small Enterprises',
    hi: '🏛️ TReDS परिपत्र 262 - सूक्ष्म और लघु उद्यमों के लिए बढ़ी हुई चालान डिस्काउंटिंग सीमा',
    gu: '🏛️ TReDS પરિપત્ર 262 - સૂક્ષ્મ અને લઘુ ઉદ્યોગો માટે વધારેલી ઇન્વોઇસ ડિસ્કાઉન્ટિંગ મર્યાદા',
  },
  announcement4: {
    en: '💼 Gujarat State Industries Policy 2025-26 - Capital Investment Subsidy and Interest Subvention windows active',
    hi: '💼 गुजरात राज्य उद्योग नीति 2025-26 - पूंजी निवेश सब्सिडी और ब्याज अनुदान विंडो सक्रिय',
    gu: '💼 ગુજરાત રાજ્ય ઉદ્યોગ નીતિ 2025-26 - મૂડી રોકાણ સબસિડી અને વ્યાજ સબવેન્શન વિન્ડો સક્રિય',
  },
  announcement5: {
    en: '⭐ ZED Certification Scheme Phase-II operational with up to 80% subsidy for MSME manufacturers',
    hi: '⭐ ZED प्रमाणन योजना चरण-II MSME निर्माताओं के लिए 80% तक सब्सिडी के साथ संचालित',
    gu: '⭐ ZED પ્રમાણન યોજના ફેઝ-II MSME ઉત્પાદકો માટે 80% સુધી સબસિડી સાથે ઓપરેશનલ',
  },
  announcement6: {
    en: '🎯 International Cooperation (IC) Scheme Guidelines 2025 updated for MSME global trade delegations',
    hi: '🎯 MSME वैश्विक व्यापार प्रतिनिधिमंडलों के लिए अंतर्राष्ट्रीय सहयोग (IC) योजना दिशानिर्देश 2025 अपडेट',
    gu: '🎯 MSME વૈશ્વિક વેપાર પ્રતિનિધિમંડળો માટે આંતરરાષ્ટ્રીય સહકાર (IC) યોજના માર્ગદર્શિકાઓ 2025 અપડેટ',
  },

  // ─── LANDING PAGE - CORE VALUE PROPOSITION ──────────────────────────────────
  officialBadge: {
    en: '100% Verified Schemes from Official Gazettes & Ministry Circulars',
    hi: 'आधिकारिक राजपत्रों और मंत्रालय परिपत्रों से 100% सत्यापित योजनाएं',
    gu: 'અધિકૃત ગેઝેટ અને મંત્રાલય પરિપત્રોમાંથી 100% ચકાસાયેલ યોજનાઓ',
  },
  heroBadge: {
    en: '100% Verified Schemes from Official Gazettes & Ministry Circulars',
    hi: 'आधिकारिक राजपत्रों और मंत्रालय परिपत्रों से 100% सत्यापित योजनाएं',
    gu: 'અધિકૃત ગેઝેટ અને મંત્રાલય પરિપત્રોમાંથી 100% ચકાસાયેલ યોજનાઓ',
  },
  heroTitle1: {
    en: 'Empowering Indian Enterprises with Verified ',
    hi: 'भारतीय उद्यमों को सशक्त बनाएं ',
    gu: 'ભારતીય ઉદ્યોગોને સશક્ત બનાવો ',
  },
  heroTitlePrefix: {
    en: 'Empowering Indian Enterprises with Verified ',
    hi: 'भारतीय उद्यमों को सशक्त बनाएं ',
    gu: 'ભારતીય ઉદ્યોગોને સશક્ત બનાવો ',
  },
  heroHighlight: {
    en: 'Government Schemes & Subsidies',
    hi: 'आधिकारिक सरकारी योजनाओं और सब्सिडी के साथ',
    gu: 'અધિકૃત સરકારી યોજનાઓ અને સબસિડી સાથે',
  },
  heroTitleHighlight: {
    en: 'Government Schemes & Subsidies',
    hi: 'आधिकारिक सरकारी योजनाओं और सब्सिडी के साथ',
    gu: 'અધિકૃત સરકારી યોજનાઓ અને સબસિડી સાથે',
  },
  heroSubtitle: {
    en: 'Access official Central & Gujarat Government schemes derived strictly from statutory PDFs and circulars. Unlock up to ₹10 Crore in collateral-free credit, 15%-35% capital subsidies, and cluster grants with verified legal compliance.',
    hi: 'वैधानिक पीडीएफ और परिपत्रों से सीधे प्राप्त आधिकारिक केंद्र और गुजरात सरकार की योजनाएं प्राप्त करें। सत्यापित कानूनी अनुपालन के साथ ₹10 करोड़ तक का बिना गारंटी ऋण, 15%-35% पूंजी सब्सिडी और क्लस्टर अनुदान प्राप्त करें।',
    gu: 'વૈધાનિક પીડીએફ અને પરિપત્રોમાંથી સીધી મેળવેલ અધિકૃત કેન્દ્ર અને ગુજરાત સરકારની યોજનાઓ મેળવો. ચકાસાયેલ કાનૂની પાલન સાથે ₹10 કરોડ સુધીની જામીન-મુક્ત ક્રેડિટ, 15%-35% મૂડી સબસિડી અને ક્લસ્ટર ગ્રાન્ટ મેળવો.',
  },
  registerEnterpriseBtn: {
    en: 'Register Enterprise',
    hi: 'उद्यम रजिस्टर करें',
    gu: 'ઉદ્યમ રજીસ્ટર કરો',
  },
  signInToAccount: {
    en: 'Sign In to Account',
    hi: 'खाते में साइन इन करें',
    gu: 'એકાઉન્ટમાં સાઇન ઇન કરો',
  },
  signInAccountBtn: {
    en: 'Sign In to Account',
    hi: 'खाते में साइन इन करें',
    gu: 'એકાઉન્ટમાં સાઇન ઇન કરો',
  },

  // ─── OFFICIAL SCHEMES FROM UPLOADED PDFS (CATALOG SECTION) ────────────────
  officialSchemesCatalog: {
    en: 'Official Schemes & Subsidies Catalog',
    hi: 'आधिकारिक योजनाएं और सब्सिडी सूची',
    gu: 'અધિકૃત યોજનાઓ અને સબસિડી સૂચિ',
  },
  officialSchemesCatalogSubtitle: {
    en: 'Extracted directly from uploaded Gazette notifications, circulars, and Ministry scheme guidelines. No outside or unverified data.',
    hi: 'अपलोड की गई राजपत्र अधिसूचनाओं, परिपत्रों और मंत्रालय दिशानिर्देशों से सीधे निकाली गई। कोई बाहरी या असत्यापित डेटा नहीं।',
    gu: 'અપલોડ કરેલી ગેઝેટ સૂચનાઓ, પરિપત્રો અને મંત્રાલય માર્ગદર્શિકામાંથી સીધા કાઢવામાં આવેલ. કોઈ બહારનો કે બિન-ચકાસાયેલ ડેટા નથી.',
  },
  filterAll: {
    en: 'All Official Schemes',
    hi: 'सभी आधिकारिक योजनाएं',
    gu: 'બધી અધિકૃત યોજનાઓ',
  },
  filterCentral: {
    en: 'Central Govt',
    hi: 'केंद्र सरकार',
    gu: 'કેન્દ્ર સરકાર',
  },
  filterGujarat: {
    en: 'Gujarat State',
    hi: 'गुजरात राज्य',
    gu: 'ગુજરાત રાજ્ય',
  },
  filterCreditGuarantee: {
    en: 'Credit Guarantee',
    hi: 'क्रेडिट गारंटी',
    gu: 'ક્રેડિટ ગેરંટી',
  },
  filterCapitalSubsidy: {
    en: 'Capital Subsidy',
    hi: 'पूंजी सब्सिडी',
    gu: 'મૂડી સબસિડી',
  },
  filterInfrastructure: {
    en: 'Infrastructure & Clusters',
    hi: 'बुनियादी ढांचा और क्लस्टर',
    gu: 'ઇન્ફ્રાસ્ટ્રક્ચર અને ક્લસ્ટર્સ',
  },
  viewDetailsBtn: {
    en: 'View Scheme Guidelines & Eligibility',
    hi: 'योजना दिशानिर्देश और पात्रता देखें',
    gu: 'યોજના માર્ગદર્શિકા અને પાત્રતા જુઓ',
  },
  maxBenefitLabel: {
    en: 'Max Financial Support',
    hi: 'अधिकतम वित्तीय सहायता',
    gu: 'મહત્તમ નાણાકીય સહાય',
  },
  officialDocRef: {
    en: 'Statutory Source Document',
    hi: 'वैधानिक स्रोत दस्तावेज',
    gu: 'વૈધાનિક સ્ત્રોત દસ્તાવેજ',
  },
  announcementsNotice1: {
    en: '⚠️ Beware of Fake Sites. For MSME Udyam Registration, visit only official portal udyamregistration.gov.in',
    hi: '⚠️ नकली साइटों से सावधान रहें। MSME उद्यम पंजीकरण के लिए, केवल आधिकारिक पोर्टल udyamregistration.gov.in पर जाएं',
    gu: '⚠️ બનાવટી સાઇટ્સથી સાવધ રહો. MSME ઉદ્યમ નોંધણી માટે, ફક્ત અધિકૃત પોર્ટલ udyamregistration.gov.in પર જાઓ',
  },
  announcementsNotice2: {
    en: '📄 New Operational Guidelines issued for SFURTI and PM-EGP Capital Subsidy Schemes 2025-26',
    hi: '📄 SFURTI और PM-EGP पूंजी सब्सिडी योजनाओं 2025-26 के लिए नए परिचालन दिशानिर्देश जारी',
    gu: '📄 SFURTI અને PM-EGP મૂડી સબસિડી યોજનાઓ 2025-26 માટે નવી ઓપરેશનલ માર્ગદર્શિકાઓ જારી',
  },
  announcementsNotice3: {
    en: '🏛️ TReDS Circular 262 - Enhanced invoice discounting limits for Micro and Small Enterprises',
    hi: '🏛️ TReDS परिपत्र 262 - सूक्ष्म और लघु उद्यमों के लिए बढ़ी हुई चालान डिस्काउंटिंग सीमा',
    gu: '🏛️ TReDS પરિપત્ર 262 - સૂક્ષ્મ અને લઘુ ઉદ્યોગો માટે વધારેલી ઇન્વોઇસ ડિસ્કાઉન્ટિંગ મર્યાદા',
  },
  announcementsNotice4: {
    en: '💼 Gujarat State Industries Policy 2025-26 - Capital Investment Subsidy and Interest Subvention windows active',
    hi: '💼 गुजरात राज्य उद्योग नीति 2025-26 - पूंजी निवेश सब्सिडी और ब्याज अनुदान विंडो सक्रिय',
    gu: '💼 ગુજરાત રાજ્ય ઉદ્યોગ નીતિ 2025-26 - મૂડી રોકાણ સબસિડી અને વ્યાજ સબવેન્શન વિન્ડો સક્રિય',
  },
  announcementsNotice5: {
    en: '⭐ ZED Certification Scheme Phase-II operational with up to 80% subsidy for MSME manufacturers',
    hi: '⭐ ZED प्रमाणन योजना चरण-II MSME निर्माताओं के लिए 80% तक सब्सिडी के साथ संचालित',
    gu: '⭐ ZED પ્રમાણન યોજના ફેઝ-II MSME ઉત્પાદકો માટે 80% સુધી સબસિડી સાથે ઓપરેશનલ',
  },
  announcementsNotice6: {
    en: '🎯 International Cooperation (IC) Scheme Guidelines 2025 updated for MSME global trade delegations',
    hi: '🎯 MSME वैश्विक व्यापार प्रतिनिधिमंडलों के लिए अंतर्राष्ट्रीय सहयोग (IC) योजना दिशानिर्देश 2025 अपडेट',
    gu: '🎯 MSME વૈશ્વિક વેપાર પ્રતિનિધિમંડળો માટે આંતરરાષ્ટ્રીય સહકાર (IC) યોજના માર્ગદર્શિકાઓ 2025 અપડેટ',
  },

  // ─── SERVICES ───────────────────────────────────────────────────────────────
  ourServices: {
    en: 'OUR SERVICES',
    hi: 'हमारी सेवाएं',
    gu: 'અમારી સેવાઓ',
  },
  servicesTitle: {
    en: 'Services We Provide to Users',
    hi: 'उपयोगकर्ताओं को प्रदान की जाने वाली सेवाएं',
    gu: 'વપરાશકર્તાઓને પૂરી પાડવામાં આવતી સેવાઓ',
  },
  servicesSubtitle: {
    en: 'Everything your enterprise needs to identify, verify, and secure government financial assistance.',
    hi: 'सरकारी वित्तीय सहायता की पहचान, सत्यापन और सुरक्षा के लिए आपके उद्यम को जो कुछ भी चाहिए।',
    gu: 'સરકારી નાણાકીય સહાયની ઓળખ, ચકાસણી અને સુરક્ષા માટે તમારા ઉદ્યમને જે કંઈ જરૂર છે.',
  },
  service1Title: {
    en: '1. AI Scheme Discovery & Matching',
    hi: '1. AI योजना खोज और मिलान',
    gu: '1. AI યોજના શોધ અને મેચિંગ',
  },
  service1Desc: {
    en: 'Instantly matches your enterprise Udyam details, plant & machinery investment, turnover, and sector against all active Central and Gujarat State schemes.',
    hi: 'आपके उद्यम के उद्यम विवरण, संयंत्र और मशीनरी निवेश, टर्नओवर और क्षेत्र को सभी सक्रिय केंद्र और गुजरात राज्य योजनाओं के साथ तुरंत मिलान करता है।',
    gu: 'તમારા ઉદ્યમના ઉદ્યમ વિગતો, પ્લાન્ટ અને મશીનરી રોકાણ, ટર્નઓવર અને ક્ષેત્રને તમામ સક્રિય કેન્દ્ર અને ગુજરાત રાજ્ય યોજનાઓ સાથે તરત જ મેચ કરે છે.',
  },
  service2Title: {
    en: '2. Multi-Scheme Stacking Optimization',
    hi: '2. बहु-योजना स्टैकिंग ऑप्टिमाइजेशन',
    gu: '2. મલ્ટી-સ્કીમ સ્ટેકિંગ ઑપ્ટિમાઇઝેશન',
  },
  service2Desc: {
    en: 'Combines credit guarantees with state capital subsidies safely and legally without triggering mutual exclusion disqualifications.',
    hi: 'आपसी बहिष्करण अयोग्यता को ट्रिगर किए बिना क्रेडिट गारंटी को राज्य पूंजी सब्सिडी के साथ सुरक्षित और कानूनी रूप से जोड़ता है।',
    gu: 'પરસ્પર બાકાત અયોગ્યતા ટ્રિગર કર્યા વિના ક્રેડિટ ગેરંટીને રાજ્ય મૂડી સબસિડી સાથે સુરક્ષિત અને કાનૂની રીતે જોડે છે.',
  },
  service3Title: {
    en: '3. Statutory Document Audit Checklist',
    hi: '3. वैधानिक दस्तावेज ऑडिट चेकलिस्ट',
    gu: '3. વૈધાનિક દસ્તાવેજ ઓડિટ ચેકલિસ્ટ',
  },
  service3Desc: {
    en: 'Generates an itemized checklist of mandatory documents (DPR, CE Valuation, Bank Sanction) extracted verbatim from government gazette releases.',
    hi: 'सरकारी राजपत्र रिलीज़ से शब्दशः निकाले गए अनिवार्य दस्तावेज़ों (DPR, CE मूल्यांकन, बैंक स्वीकृति) की एक विस्तृत चेकलिस्ट तैयार करता है।',
    gu: 'સરકારી ગેઝેટ રિલીઝમાંથી શબ્દશઃ કાઢવામાં આવેલા ફરજિયાત દસ્તાવેજો (DPR, CE મૂલ્યાંકન, બેંક મંજૂરી) ની વિગતવાર ચેકલિસ્ટ તૈયાર કરે છે.',
  },
  service4Title: {
    en: '4. Live Policy & Gazette Radar',
    hi: '4. लाइव नीति और गजट रडार',
    gu: '4. લાઇવ નીતિ અને ગેઝેટ રડાર',
  },
  service4Desc: {
    en: 'Monitors ongoing gazette notifications and circulars, notifying your business when deadlines extend or budget limits expand.',
    hi: 'चल रही राजपत्र अधिसूचनाओं और परिपत्रों की निगरानी करता है, जब समय सीमा बढ़ती है या बजट सीमा का विस्तार होता है तो आपके व्यवसाय को सूचित करता है।',
    gu: 'ચાલુ ગેઝેટ સૂચનાઓ અને પરિપત્રોનું નિરીક્ષણ કરે છે, જ્યારે સમયમર્યાદા વધે અથવા બજેટ મર્યાદા વધે ત્યારે તમારા વ્યવસાયને સૂચિત કરે છે.',
  },
  service5Title: {
    en: '5. Clause-Level Legal Citations',
    hi: '5. खंड-स्तरीय कानूनी उद्धरण',
    gu: '5. કલમ-સ્તરીય કાનૂની ટાંકણ',
  },
  service5Desc: {
    en: 'Provides exact operational guideline paragraph and circular citations for every scheme so banks and DIC officers approve without delays.',
    hi: 'हर योजना के लिए सटीक परिचालन दिशानिर्देश पैराग्राफ और परिपत्र उद्धरण प्रदान करता है ताकि बैंक और DIC अधिकारी बिना देरी के मंजूरी दें।',
    gu: 'દરેક યોજના માટે ચોક્કસ ઓપરેશનલ માર્ગદર્શિકા ફકરો અને પરિપત્ર ટાંકણ પ્રદાન કરે છે જેથી બેંકો અને DIC અધિકારીઓ વિલંબ વિના મંજૂર કરે.',
  },
  service6Title: {
    en: '6. End-to-End Application Guidance',
    hi: '6. शुरू से अंत तक आवेदन मार्गदर्शन',
    gu: '6. શરૂથી અંત સુધી અરજી માર્ગદર્શન',
  },
  service6Desc: {
    en: 'A structured roadmap guiding your team from pre-qualification to portal submission and DBT subsidy disbursement.',
    hi: 'पूर्व-योग्यता से पोर्टल सबमिशन और DBT सब्सिडी वितरण तक आपकी टीम का मार्गदर्शन करने वाला एक संरचित रोडमैप।',
    gu: 'પ્રી-ક્વોલિફિકેશનથી પોર્ટલ સબમિશન અને DBT સબસિડી વિતરણ સુધી તમારી ટીમને માર્ગદર્શન આપતો સંરચિત રોડમેપ.',
  },

  // ─── BENEFITS ───────────────────────────────────────────────────────────────
  benefits: {
    en: 'BENEFITS',
    hi: 'लाभ',
    gu: 'લાભો',
  },
  benefitsTitle: {
    en: 'Benefits Provided to MSME Users',
    hi: 'MSME उपयोगकर्ताओं को प्रदान किए जाने वाले लाभ',
    gu: 'MSME વપરાશકર્તાઓને પૂરા પાડવામાં આવતા લાભો',
  },
  benefitsSubtitle: {
    en: 'Why MSME founders, CFOs, and business owners choose UdyamNiti over manual research.',
    hi: 'MSME संस्थापक, CFO और व्यवसाय मालिक मैनुअल रिसर्च की जगह UdyamNiti क्यों चुनते हैं।',
    gu: 'MSME સ્થાપકો, CFOs અને વ્યવસાય માલિકો મેન્યુઅલ સંશોધન કરતાં UdyamNiti શા માટે પસંદ કરે છે.',
  },
  benefit1Title: { en: 'Non-Dilutive Capital Access', hi: 'गैर-डाइल्यूटिव पूंजी पहुंच', gu: 'નોન-ડાયલ્યુટિવ મૂડી ઍક્સેસ' },
  benefit1Desc: { en: 'Claim capital subsidies, interest subvention, and collateral guarantees without losing company equity or pledging personal family property.', hi: 'कंपनी इक्विटी खोए बिना या व्यक्तिगत संपत्ति गिरवी रखे बिना पूंजी सब्सिडी, ब्याज अनुदान और जमानत गारंटी का दावा करें।', gu: 'કંપનીની ઇક્વિટી ગુમાવ્યા વિના અથવા વ્યક્તિગત મિલકત ગીરવે મૂક્યા વિના મૂડી સબસિડી, વ્યાજ સબવેન્શન અને જામીન ગેરંટીનો દાવો કરો.' },
  benefit2Title: { en: 'Minutes, Not Weeks', hi: 'मिनट, सप्ताह नहीं', gu: 'મિનિટો, અઠવાડિયા નહીં' },
  benefit2Desc: { en: 'Replace weeks of reading complex 80-page government PDF guidelines with an automated 2-minute scheme eligibility scan.', hi: 'जटिल 80-पृष्ठ सरकारी PDF दिशानिर्देशों को पढ़ने के हफ्तों को स्वचालित 2-मिनट योजना पात्रता स्कैन से बदलें।', gu: 'જટિલ 80-પૃષ્ઠ સરકારી PDF માર્ગદર્શિકાઓ વાંચવાના અઠવાડિયાને ઓટોમેટેડ 2-મિનિટ યોજના પાત્રતા સ્કેન સાથે બદલો.' },
  benefit3Title: { en: 'First-Time Application Approval', hi: 'पहली बार आवेदन स्वीकृति', gu: 'પ્રથમ વખત અરજી મંજૂરી' },
  benefit3Desc: { en: 'Pre-validated document checklists prevent missing paperwork mistakes that cause 68% of MSME government claims to stall.', hi: 'पूर्व-सत्यापित दस्तावेज़ चेकलिस्ट लापता कागजी कार्रवाई की गलतियों को रोकती है जो 68% MSME सरकारी दावों को रोकती हैं।', gu: 'પૂર્વ-ચકાસાયેલ દસ્તાવેજ ચેકલિસ્ટ ખૂટતી કાગળકાર્યની ભૂલોને અટકાવે છે જે 68% MSME સરકારી દાવાઓને અટકાવે છે.' },
  benefit4Title: { en: 'Multi-Scheme Advantage', hi: 'बहु-योजना लाभ', gu: 'મલ્ટી-સ્કીમ ફાયદો' },
  benefit4Desc: { en: 'Learn how to legally combine Gujarat State assistance with Central schemes to maximize total capital recovery for your factory.', hi: 'अपने कारखाने के लिए कुल पूंजी वसूली को अधिकतम करने के लिए गुजरात राज्य सहायता को केंद्रीय योजनाओं के साथ कानूनी रूप से कैसे जोड़ें, यह सीखें।', gu: 'તમારી ફેક્ટરી માટે કુલ મૂડી પુનઃપ્રાપ્તિ વધારવા ગુજરાત રાજ્ય સહાયને કેન્દ્રીય યોજનાઓ સાથે કાયદેસર રીતે કેવી રીતે જોડવી તે શીખો.' },
  benefit5Title: { en: 'Zero AI Hallucinations', hi: 'शून्य AI भ्रम', gu: 'ઝીરો AI ભ્રમ' },
  benefit5Desc: { en: 'Every single subsidy number, percentage, and condition is mathematically verified against the official gazette notifications.', hi: 'हर एक सब्सिडी संख्या, प्रतिशत और शर्त को आधिकारिक राजपत्र अधिसूचनाओं के विरुद्ध गणितीय रूप से सत्यापित किया जाता है।', gu: 'દરેક સબસિડી નંબર, ટકાવારી અને શરત સત્તાવાર ગેઝેટ સૂચનાઓ સામે ગાણિતિક રીતે ચકાસવામાં આવે છે.' },
  benefit6Title: { en: 'Never Miss a Deadline', hi: 'कोई समय सीमा न चूकें', gu: 'કોઈ ડેડલાઇન ચૂકો નહીં' },
  benefit6Desc: { en: 'Automated monitoring keeps your business notified of annual fiscal year cutoffs and special cluster incentive windows.', hi: 'स्वचालित निगरानी आपके व्यवसाय को वार्षिक वित्तीय वर्ष कटऑफ और विशेष क्लस्टर प्रोत्साहन विंडो के बारे में सूचित रखती है।', gu: 'ઓટોમેટેડ મોનિટરિંગ તમારા વ્યવસાયને વાર્ષિક નાણાકીય વર્ષ કટ-ઑફ અને ખાસ ક્લસ્ટર પ્રોત્સાહન વિન્ડો વિશે જાણ કરે છે.' },

  // ─── FAQ ─────────────────────────────────────────────────────────────────────
  faq: {
    en: 'Frequently Asked Questions',
    hi: 'अक्सर पूछे जाने वाले प्रश्न',
    gu: 'વારંવાર પૂછાતા પ્રશ્નો',
  },
  faqSubtitle: {
    en: 'Answers to questions about accessing the platform and scheme qualification.',
    hi: 'प्लेटफॉर्म और योजना योग्यता तक पहुंचने के बारे में प्रश्नों के उत्तर।',
    gu: 'પ્લેટફોર્મ અને યોજના લાયકાત ઍક્સેસ કરવા વિશેના પ્રશ્નોના જવાબો.',
  },
  faq1Q: { en: 'How do I access the Dashboard?', hi: 'मैं डैशबोर्ड कैसे एक्सेस करूं?', gu: 'હું ડેશબોર્ડ કેવી રીતે ઍક્સેસ કરું?' },
  faq1A: { en: 'Click "Register" or "Sign In" at the top of the page. After filling in your enterprise details and clicking submit, you are instantly redirected to the Schemes Dashboard.', hi: 'पेज के शीर्ष पर "रजिस्टर" या "साइन इन" पर क्लिक करें। अपने उद्यम विवरण भरने और सबमिट पर क्लिक करने के बाद, आपको तुरंत योजना डैशबोर्ड पर रीडायरेक्ट किया जाता है।', gu: 'પૃષ્ઠની ટોચ પર "રજીસ્ટર" અથવા "સાઇન ઇન" પર ક્લિક કરો. તમારા ઉદ્યમની વિગતો ભરીને સબમિટ ક્લિક કર્યા પછી, તમને તરત જ યોજના ડેશબોર્ડ પર રીડાયરેક્ટ કરવામાં આવે છે.' },
  faq2Q: { en: 'Can my business combine Gujarat State schemes with Central Government schemes?', hi: 'क्या मेरा व्यवसाय गुजरात राज्य योजनाओं को केंद्र सरकार की योजनाओं के साथ जोड़ सकता है?', gu: 'શું મારો વ્યવસાય ગુજરાત રાજ્ય યોજનાઓને કેન્દ્ર સરકારની યોજનાઓ સાથે જોડી શકે છે?' },
  faq2A: { en: 'Yes! Our multi-scheme stacking engine analyzes whether pairing Central schemes (such as CGTMSE credit guarantee) with Gujarat state subsidies is legally permissible without mutual exclusion penalties.', hi: 'हां! हमारा बहु-योजना स्टैकिंग इंजन विश्लेषण करता है कि केंद्रीय योजनाओं (जैसे CGTMSE क्रेडिट गारंटी) को गुजरात राज्य सब्सिडी के साथ जोड़ना आपसी बहिष्करण दंड के बिना कानूनी रूप से अनुमत है या नहीं।', gu: 'હા! અમારું મલ્ટી-સ્કીમ સ્ટેકિંગ એન્જિન વિશ્લેષણ કરે છે કે કેન્દ્રીય યોજનાઓ (જેમ કે CGTMSE ક્રેડિટ ગેરંટી) ને ગુજરાત રાજ્ય સબસિડી સાથે જોડવું પરસ્પર બાકાત દંડ વિના કાયદેસર રીતે અનુમતિ છે કે નહીં.' },
  faq3Q: { en: 'Do I need an active Udyam registration to get started?', hi: 'क्या शुरू करने के लिए मुझे सक्रिय उद्यम पंजीकरण की आवश्यकता है?', gu: 'શરૂ કરવા માટે મારે સક્રિય ઉદ્યમ નોંધણીની જરૂર છે?' },
  faq3A: { en: 'No. You can register using your approximate plant & machinery investment, turnover, and sector. Our system will evaluate what you qualify for and guide you on obtaining your official certificate.', hi: 'नहीं। आप अपने अनुमानित संयंत्र और मशीनरी निवेश, टर्नओवर और क्षेत्र का उपयोग करके पंजीकरण कर सकते हैं। हमारा सिस्टम मूल्यांकन करेगा कि आप किसके लिए योग्य हैं और आपका आधिकारिक प्रमाणपत्र प्राप्त करने में आपका मार्गदर्शन करेगा।', gu: 'ના. તમે તમારા અંદાજિત પ્લાન્ટ અને મશીનરી રોકાણ, ટર્નઓવર અને ક્ષેત્રનો ઉપયોગ કરીને નોંધણી કરી શકો છો. અમારી સિસ્ટમ મૂલ્યાંકન કરશે કે તમે શેના માટે લાયક છો અને તમારું સત્તાવાર પ્રમાણપત્ર મેળવવામાં માર્ગદર્શન કરશે.' },
  faq4Q: { en: 'How are scheme PDFs parsed into the platform?', hi: 'योजना PDFs को प्लेटफॉर्म में कैसे पार्स किया जाता है?', gu: 'યોજના PDFs ને પ્લેટફોર્મમાં કેવી રીતે પાર્સ કરવામાં આવે છે?' },
  faq4A: { en: 'Our platform ingests official gazette guidelines and PDF circulars from the backend scheme directory, automatically structuring eligibility criteria, documents, and subsidies so you never have to decipher bureaucratic jargon manually.', hi: 'हमारा प्लेटफॉर्म बैकएंड योजना निर्देशिका से आधिकारिक राजपत्र दिशानिर्देश और PDF परिपत्रों को ग्रहण करता है, स्वचालित रूप से पात्रता मानदंड, दस्तावेज और सब्सिडी की संरचना करता है ताकि आपको कभी भी नौकरशाही शब्दजाल को मैन्युअल रूप से समझने की आवश्यकता न हो।', gu: 'અમારું પ્લેટફોર્મ બેકએન્ડ યોજના ડિરેક્ટરીમાંથી સત્તાવાર ગેઝેટ માર્ગદર્શિકાઓ અને PDF પરિપત્રોને ઇન્જેસ્ટ કરે છે, આપોઆપ પાત્રતા માપદંડો, દસ્તાવેજો અને સબસિડીની રચના કરે છે જેથી તમારે ક્યારેય અમલદારશાહી ભાષાને મેન્યુઅલી સમજવાની જરૂર ન પડે.' },

  // ─── CTA / FOOTER ───────────────────────────────────────────────────────────
  ctaTitle: {
    en: 'Ready to Claim Your Eligible Subsidies?',
    hi: 'अपनी पात्र सब्सिडी का दावा करने के लिए तैयार हैं?',
    gu: 'તમારી પાત્ર સબસિડીનો દાવો કરવા તૈયાર છો?',
  },
  ctaSubtitle: {
    en: 'Register your enterprise in 30 seconds and enter the Schemes Dashboard directly.',
    hi: '30 सेकंड में अपना उद्यम रजिस्टर करें और सीधे योजना डैशबोर्ड में प्रवेश करें।',
    gu: '30 સેકન્ડમાં તમારું ઉદ્યમ રજીસ્ટર કરો અને સીધા યોજના ડેશબોર્ડમાં પ્રવેશ કરો.',
  },
  registerAndGo: {
    en: 'Register & Go to Dashboard',
    hi: 'रजिस्टर करें और डैशबोर्ड पर जाएं',
    gu: 'રજીસ્ટર કરો અને ડેશબોર્ડ પર જાઓ',
  },
  footerDesc: {
    en: "India's premier AI-powered Government Schemes, Subsidies & Policy Intelligence Platform. Accelerating MSME industrial growth with verifiable gazette citations, collateral-free credit, and statutory document readiness.",
    hi: 'भारत का प्रमुख AI-संचालित सरकारी योजनाएं, सब्सिडी और नीति बुद्धिमत्ता प्लेटफॉर्म। सत्यापन योग्य राजपत्र उद्धरणों, जमानत-मुक्त ऋण और वैधानिक दस्तावेज तैयारी के साथ MSME औद्योगिक विकास को गति प्रदान करना।',
    gu: 'ભારતનું અગ્રણી AI-સંચાલિત સરકારી યોજનાઓ, સબસિડી અને નીતિ ઇન્ટેલિજન્સ પ્લેટફોર્મ. ચકાસી શકાય તેવા ગેઝેટ ટાંકણ, જામીન-મુક્ત ક્રેડિટ અને વૈધાનિક દસ્તાવેજ તૈયારી સાથે MSME ઔદ્યોગિક વૃદ્ધિને વેગ આપવો.',
  },
  footerMinistry: { en: 'Ministry', hi: 'मंत्रालय', gu: 'મંત્રાલય' },
  footerOfferings: { en: 'Offerings', hi: 'प्रस्ताव', gu: 'ઓફરિંગ્સ' },
  footerHelpline: { en: 'Helpline & Connect', hi: 'हेल्पलाइन और संपर्क', gu: 'હેલ્પલાઇન અને સંપર્ક' },
  footerCopyright: {
    en: 'UdyamNiti - Government of India & Gujarat State Schemes Intelligence',
    hi: 'UdyamNiti - भारत सरकार और गुजरात राज्य योजना बुद्धिमत्ता',
    gu: 'UdyamNiti - ભારત સરકાર અને ગુજરાત રાજ્ય યોજના ઇન્ટેલિજન્સ',
  },
  footerCompliance: {
    en: 'Standard WCAG 2.1 AA Compliant - Clean Light Government Theme',
    hi: 'WCAG 2.1 AA मानक अनुपालन - स्वच्छ सरकारी थीम',
    gu: 'WCAG 2.1 AA ધોરણ અનુપાલન - સ્વચ્છ સરકારી થીમ',
  },
  accessSchemesPortal: {
    en: 'Access Schemes Portal',
    hi: 'योजना पोर्टल एक्सेस करें',
    gu: 'યોજના પોર્ટલ ઍક્સેસ કરો',
  },
  officialGateway: {
    en: 'Official National Gateway for Central and Gujarat State MSME Incentives.',
    hi: 'केंद्र और गुजरात राज्य MSME प्रोत्साहन के लिए आधिकारिक राष्ट्रीय पोर्टल।',
    gu: 'કેન્દ્ર અને ગુજરાત રાજ્ય MSME પ્રોત્સાહન માટે અધિકૃત રાષ્ટ્રીય પોર્ટલ.',
  },
  // Footer link items
  citizenCharter: { en: 'Citizen Charter', hi: 'नागरिक चार्टर', gu: 'નાગરિક ચાર્ટર' },
  annualReports: { en: 'Annual Reports', hi: 'वार्षिक रिपोर्ट', gu: 'વાર્ષિક અહેવાલો' },
  creditGuarantees: { en: 'Credit Guarantees', hi: 'क्रेडिट गारंटी', gu: 'ક્રેડિટ ગેરંટી' },
  capitalSubsidies: { en: 'Capital Subsidies', hi: 'पूंजी सब्सिडी', gu: 'મૂડી સબસિડી' },
  clusterDevelopment: { en: 'Cluster Development', hi: 'क्लस्टर विकास', gu: 'ક્લસ્ટર વિકાસ' },
  zedCertification: { en: 'ZED Certification', hi: 'ZED प्रमाणन', gu: 'ZED પ્રમાણન' },

  // ─── MODAL TITLES ───────────────────────────────────────────────────────────
  modalAboutTitle: {
    en: 'About Ministry of Micro, Small & Medium Enterprises',
    hi: 'सूक्ष्म, लघु और मध्यम उद्यम मंत्रालय के बारे में',
    gu: 'સૂક્ષ્મ, લઘુ અને મધ્યમ ઉદ્યમ મંત્રાલય વિશે',
  },
  modalPerformanceTitle: {
    en: 'Our Performance & National MSME Milestones',
    hi: 'हमारा प्रदर्शन और राष्ट्रीय MSME मील के पत्थर',
    gu: 'અમારું પ્રદર્શન અને રાષ્ટ્રીય MSME સીમાચિહ્નો',
  },
  modalPhotosTitle: {
    en: 'Media Gallery - Photos',
    hi: 'मीडिया गैलरी - फोटो',
    gu: 'મીડિયા ગેલેરી - ફોટો',
  },
  modalVideosTitle: {
    en: 'Media Gallery - Videos',
    hi: 'मीडिया गैलरी - वीडियो',
    gu: 'મીડિયા ગેલેરી - વીડિયો',
  },
  modalBrochuresTitle: {
    en: 'Official Policy Guidelines & Scheme Brochures',
    hi: 'आधिकारिक नीति दिशानिर्देश और योजना ब्रोशर',
    gu: 'અધિકૃત નીતિ માર્ગદર્શિકાઓ અને યોજના બ્રોશર',
  },
  modalContactTitle: {
    en: 'Contact Directory & MSME Facilitation Centers',
    hi: 'संपर्क निर्देशिका और MSME सुविधा केंद्र',
    gu: 'સંપર્ક ડિરેક્ટરી અને MSME સુવિધા કેન્દ્રો',
  },
  modalRtiTitle: {
    en: 'Right to Information (RTI) Act, 2005',
    hi: 'सूचना का अधिकार (RTI) अधिनियम, 2005',
    gu: 'માહિતી અધિકાર (RTI) અધિનિયમ, 2005',
  },
  // ─── SCHEME DETAIL & DASHBOARD ──────────────────────────────────────────────
  backToSchemes: { en: 'Back to Schemes', hi: 'योजनाओं पर वापस', gu: 'યોજનાઓ પર પાછા જાઓ' },
  schemeOverview: { en: 'Scheme Overview', hi: 'योजना अवलोकन', gu: 'યોજના ઝાંખી' },
  whoIsEligible: { en: 'Who is Eligible', hi: 'कौन पात्र है', gu: 'કોણ પાત્ર છે' },
  benefitsFinancialAssistance: { en: 'Benefits & Financial Assistance', hi: 'लाभ और वित्तीय सहायता', gu: 'લાભો અને નાણાકીય સહાય' },
  requiredDocuments: { en: 'Required Documents', hi: 'आवश्यक दस्तावेज', gu: 'જરૂરી દસ્તાવેજો' },
  applicationProcedure: { en: 'Application Procedure', hi: 'आवेदन प्रक्रिया', gu: 'અરજી પ્રક્રિયા' },
  allDetails: { en: 'All Details', hi: 'सभी विवरण', gu: 'બધી વિગતો' },
  downloadChecklist: { en: 'Download Checklist', hi: 'चेकलिस्ट डाउनलोड करें', gu: 'ચેકલિસ્ટ ડાઉનલોડ કરો' },
  applyOnOfficialPortal: { en: 'Apply on Official Portal', hi: 'आधिकारिक पोर्टल पर आवेदन करें', gu: 'સત્તાવાર પોર્ટલ પર અરજી કરો' },
  eligibilityCriteria: { en: 'Eligibility Criteria', hi: 'पात्रता मापदंड', gu: 'પાત્રતા માપદંડ' },
  eligible: { en: 'Eligible', hi: 'पात्र', gu: 'લાયક' },
  notEligible: { en: 'Not Eligible', hi: 'अपात्र', gu: 'અપાત્ર' },
  maximumBenefit: { en: 'Maximum Benefit', hi: 'अधिकतम लाभ', gu: 'મહત્તમ લાભ' },
  subsidyRate: { en: 'Subsidy Rate', hi: 'सब्सिडी दर', gu: 'સબસિડી દર' },
  nodalAgency: { en: 'Nodal Agency', hi: 'नोडल एजेंसी', gu: 'નોડલ એજન્સી' },
  officialGazette: { en: 'Official Gazette', hi: 'आधिकारिक राजपत्र', gu: 'સત્તાવાર ગેઝેટ' },
  stepByStepApplication: { en: 'Step-by-Step Application Procedure', hi: 'चरण-दर-चरण आवेदन प्रक्रिया', gu: 'પગલાંવાર અરજી પ્રક્રિયા' },
  verifiedOfficialNotice: { en: 'Statutory Verification & Legal Proof', hi: 'वैधानिक सत्यापन और कानूनी प्रमाण', gu: 'વૈધાનિક ચકાસણી અને કાનૂની પુરાવો' },
  documentsChecklistDesc: { en: 'Check off each document as you prepare your application dossier.', hi: 'अपने आवेदन डोजियर को तैयार करते समय प्रत्येक दस्तावेज़ पर निशान लगाएं।', gu: 'તમારી અરજી ડોઝિયર તૈયાર કરતી વખતે દરેક દસ્તાવેજ પર નિશાન કરો.' },

  // ─── AUTHENTICATION (LOGIN / REGISTER) ──────────────────────────────────────
  welcomeBack: { en: 'Welcome Back', hi: 'वापसी पर स्वागत है', gu: 'પાછા સ્વાગત છે' },
  loginToAccount: { en: 'Sign in to access your enterprise subsidies', hi: 'अपनी उद्यम सब्सिडी तक पहुँचने के लिए साइन इन करें', gu: 'તમારા ઉદ્યમની સબસિડીઓ ઍક્સેસ કરવા સાઇન ઇન કરો' },
  emailAddress: { en: 'Official Email Address', hi: 'आधिकारिक ईमेल पता', gu: 'સત્તાવાર ઇમેઇલ સરનામું' },
  password: { en: 'Password', hi: 'पासवर्ड', gu: 'પાસવર્ડ' },
  enterPassword: { en: 'Enter your password', hi: 'अपना पासवर्ड दर्ज करें', gu: 'તમારો પાસવર્ડ દાખલ કરો' },
  rememberMe: { en: 'Remember this device', hi: 'इस डिवाइस को याद रखें', gu: 'આ ઉપકરણ યાદ રાખો' },
  forgotPassword: { en: 'Forgot Password?', hi: 'पासवर्ड भूल गए?', gu: 'પાસવર્ડ ભૂલી ગયા છો?' },
  dontHaveAccount: { en: "Don't have an enterprise account?", hi: 'क्या उद्यम खाता नहीं है?', gu: 'ઉદ્યમ ખાતું નથી?' },
  registerHeading: { en: 'Enterprise Registration', hi: 'उद्यम पंजीकरण', gu: 'ઉદ્યમ નોંધણી' },
  registerSubheading: { en: 'Unlock verified government subsidies and collateral-free capital', hi: 'सत्यापित सरकारी सब्सिडी और जमानत-मुक्त पूंजी प्राप्त करें', gu: 'ચકાસાયેલ સરકારી સબસિડી અને જામીન-મુક્ત મૂડી અનલૉક કરો' },
  fullName: { en: 'Authorized Representative Name', hi: 'अधिकृत प्रतिनिधि का नाम', gu: 'અધિકૃત પ્રતિનિધિનું નામ' },
  enterpriseName: { en: 'Enterprise / Firm Name', hi: 'उद्यम / फर्म का नाम', gu: 'ઉદ્યમ / પેઢીનું નામ' },
  phone: { en: 'Mobile Number', hi: 'मोबाइल नंबर', gu: 'મોબાઇલ નંબર' },
  udyamNumber: { en: 'Udyam Registration Number (Optional)', hi: 'उद्यम पंजीकरण संख्या (वैकल्पिक)', gu: 'ઉદ્યમ નોંધણી નંબર (વૈકલ્પિક)' },
  investmentInPlant: { en: 'Plant & Machinery Investment (₹)', hi: 'संयंत्र और मशीनरी निवेश (₹)', gu: 'પ્લાન્ટ અને મશીનરી રોકાણ (₹)' },
  annualTurnover: { en: 'Annual Turnover (₹)', hi: 'वार्षिक टर्नओवर (₹)', gu: 'વાર્ષિક ટર્નઓવર (₹)' },
  alreadyRegistered: { en: 'Already registered?', hi: 'पहले से पंजीकृत हैं?', gu: 'પહેલેથી નોંધાયેલા છો?' },
  selectLanguage: { en: 'Select Language', hi: 'भाषा चुनें', gu: 'ભાષા પસંદ કરો' },
} as const

export type TranslationKey = keyof typeof translations

export function t(key: TranslationKey, lang: Language): string {
  return translations[key]?.[lang] || translations[key]?.['en'] || key
}
