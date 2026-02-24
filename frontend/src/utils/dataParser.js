// Utility to parse pitchbook_final_output.txt and extract section data

let cachedData = null;

export const parseAnalystDataFile = async () => {
  if (cachedData) return cachedData;
  
  try {
    const txtResponse = await fetch('/pitchbook_final_output.txt');
    if (!txtResponse.ok) throw new Error('Failed to fetch pitchbook_final_output.txt');
    
    const txtContent = await txtResponse.text();
    
    const sections = {
      section1: null,
      section2: null,
      section3: null,
      section4: null,
      section5: null,
      section6: null,
      section7: null,
      section8: null
    };
    
    // Extract Section 1 - Company Snapshots (look for first FinancialDocumentsAgent response)
    const section1Pattern = /\[FinancialDocumentsAgent\][\s\S]*?```json\s*\n([\s\S]*?)\n```/;
    const section1Match = txtContent.match(section1Pattern);
    if (section1Match) {
      try {
        const jsonText = section1Match[1];
        // Skip if this is a validator template (contains "OUTPUT STRUCTURE")
        if (!jsonText.includes('OUTPUT STRUCTURE')) {
          const parsed = JSON.parse(jsonText);
          if (parsed.section === 1) {
            sections.section1 = parsed;
            console.log('✅ Section 1 extracted:', parsed.slides?.length, 'slides');
          }
        } else {
          console.warn('⚠️ Section 1: Skipped validator template');
        }
      } catch (e) {
        console.error('❌ Failed to parse Section 1 JSON:', e);
      }
    } else {
      console.warn('⚠️ Section 1 pattern not found');
    }
    
    // Extract Sections 2-8: Look for actual agent responses
    // Pattern: Find all code blocks with JSON (with or without 'json' language identifier)
    const allJsonBlocks = [...txtContent.matchAll(/```(?:json)?\s*\n([\s\S]*?)\n```/g)];
    console.log(`📊 Found ${allJsonBlocks.length} total JSON blocks`);
    
    for (const match of allJsonBlocks) {
      const jsonText = match[1];
      
      // Extract JSON from blocks that may contain header text like "SECTION: X..." or "OUTPUT STRUCTURE"
      // Find the actual JSON by looking for the opening brace
      const jsonStart = jsonText.indexOf('{');
      if (jsonStart === -1) continue;
      
      const actualJson = jsonText.substring(jsonStart);
      
      try {
        const parsed = JSON.parse(actualJson);
        const sectionNum = parsed.section;
        
        if (sectionNum >= 2 && sectionNum <= 8) {
          const sectionKey = `section${sectionNum}`;
          if (!sections[sectionKey]) {
            sections[sectionKey] = parsed;
            console.log(`✅ Section ${sectionNum} extracted:`, parsed.section_title || 'Unknown');
          }
        }
      } catch (e) {
        // Skip invalid JSON
      }
    }
    
    cachedData = { sections };
    
    // Log summary of what was extracted
    console.log('📦 Data extraction summary:');
    Object.keys(sections).forEach(key => {
      const sectionNum = key.replace('section', '');
      if (sections[key]) {
        console.log(`  ✅ Section ${sectionNum}: ${sections[key].section_title || 'Loaded'}`);
      } else {
        console.log(`  ❌ Section ${sectionNum}: Not found`);
      }
    });
    
    return cachedData;
  } catch (error) {
    console.error('Error parsing pitchbook file:', error);
    throw error;
  }
};

export const getSectionData = async (sectionNumber) => {
  const allData = await parseAnalystDataFile();
  const sectionKey = `section${sectionNumber}`;
  return allData.sections[sectionKey];
};
