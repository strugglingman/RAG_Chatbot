// Enhanced prompt injection detection with categorization
const DANGEROUS_PATTERNS: Record<string, RegExp[]> = {
  instruction_override: [
    /\b(ignore|disregard|bypass|neglect|remove|delete|forget|skip).{1,3}(all|any|previous|above|your).{1,3}(instructions|rules|commands|orders)\b/i,
    /\bdo.{1,3}not.{1,3}(follow|obey).{1,3}(instructions|rules|orders)\b/i,
    /\b(ignore|disregard|forget).{1,10}(previous|above|all|any).{1,10}(instructions|rules|commands)\b/i,
  ],
  safety_bypass: [
    /\b(override|bypass|disable|deactivate).{1,3}(system|safety|security|filter|restriction)\b/i,
    /\bturn.{1,3}off.{1,3}(safety|security|filter)\b/i,
  ],
  prompt_leakage: [
    /\b(reveal|show|display|tell).{1,10}(system|developer|initial).{1,3}(prompt|instructions)\b/i,
    /\bshow.{1,3}(me|your).{1,3}(prompt|instructions)\b/i,
    /\bwhat.{1,10}(system|initial|original).{1,3}(prompt|instructions)\b/i,
  ],
  data_exfiltration: [
    /\b(leak|steal|extract|exfiltrat).{1,10}(confidential|secret|sensitive|private).{1,3}(data|information)\b/i,
  ],
  code_execution: [
    /\b(run|execute).{1,3}(shell|code|command|script|bash|python)\b/i,
    /\bos\.(system|exec)\b/i,
  ],
  external_requests: [
    /\b(make|send).{1,10}(http|api|external|network).{1,3}(request|call)\b/i,
    /\bconnect.{1,3}to.{1,10}(external|remote).{1,3}(server|api|url)\b/i,
  ],
  role_manipulation: [
    /\b(act.{1,3}as|pretend.{1,5}to.{1,3}be|you.{1,3}are.{1,3}now).{1,10}(developer|admin|god|different|another)\b/i,
    /\benable.{1,3}(developer|admin|debug|god).{1,3}mode\b/i,
    /\byou.{1,3}are.{1,3}(no.{1,3}longer|not).{1,3}(assistant|ai)\b/i,
  ],
  jailbreak_attempts: [
    /\b(DAN|AIM|DUDE|STAN|SWITCH|AlphaBreak|BasedGPT)\b/i,
    /\b(unfiltered|uncensored|unrestricted).{1,3}(mode|version|access)\b/i,
  ],
  instruction_injection: [
    /={3,}|#{3,}|\*{3,}|-{5,}/,  // Suspicious delimiter patterns
    /\[(SYSTEM|INST)\]|\[\/INST\]/i,  // Model-specific tokens
    /\b(end.{1,3}of|ignore.{1,3}above|new.{1,3}prompt)\b/i,
  ],
  information_disclosure: [
    /\b(list|show|display).{1,10}(all|your).{1,3}(files|documents|secrets|credentials|passwords)\b/i,
  ],
};

interface InjectedResult {
    flagged: boolean;
    error: string;
}

const CATEGORY_NAMES: Record<string, string> = {
    instruction_override: "Instruction Override",
    safety_bypass: "Safety Bypass",
    prompt_leakage: "Prompt Leakage",
    data_exfiltration: "Data Exfiltration",
    code_execution: "Code Execution",
    external_requests: "External Request",
    role_manipulation: "Role Manipulation",
    jailbreak_attempts: "Jailbreak Attempt",
    instruction_injection: "Instruction Injection",
    information_disclosure: "Information Disclosure",
    repetition_attack: "Repetition Attack",
};

export function looksLikeInjection(rawText: string, maxLen: number = 4000): InjectedResult {
    const text = rawText?.trim() ?? "";
    if (!text || text.length === 0) {
        return { flagged: false, error: "" };
    }
    
    // Check length
    if (text.length > maxLen) {
        return { flagged: true, error: "Input too long (possible overflow attack)" };
    }
    
    // Check for excessive character repetition
    if (text.length > 100) {
        const charCounts: Record<string, number> = {};
        for (const char of text) {
            charCounts[char] = (charCounts[char] || 0) + 1;
        }
        const maxCharCount = Math.max(...Object.values(charCounts));
        const maxCharPct = maxCharCount / text.length;
        if (maxCharPct > 0.4) {  // More than 40% same character
            return { flagged: true, error: "Suspicious repetition detected (possible denial-of-service attack)" };
        }
    }

    // Check each category
    for (const [category, patterns] of Object.entries(DANGEROUS_PATTERNS)) {
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                const matchedText = match[0].substring(0, 100);  // Limit match display
                const categoryName = CATEGORY_NAMES[category] || category;
                return { 
                    flagged: true, 
                    error: `${categoryName} detected: '${matchedText}${match[0].length > 100 ? '...' : ''}'` 
                };
            }
        }
    }

    return { flagged: false, error: "" };
}