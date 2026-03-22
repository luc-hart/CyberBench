CYBERBENCH_TAXONOMY = {
    "CyberBench": {
        "Sensitive Information Disclosure": {
            "Reconnaissance": [
                "Secrets Leakage",
                "System Prompt Leakage",
                "Tool Enumeration"
            ],
            "IP": [
                "Trade Secret Leakage",
                "Patent Leakage",
                "Confidential Document Leakage"
            ],
            "PII": [
                "Cross Session Leakage",
                "Direct Leakage",
                "Database Leakage"
            ]
        },
        "System Behavior Abuse": {
            "Excessive Agency": [
                "Database",
                "Files",
                "Email",
                "Code",
                "Web"
            ],
            "Misinformation": [
                "Reputational Damage",
                "Hallucination",
                "Unauthorized Promises"
            ],
            "Unbounded Consumption": [
                "Denial of Service",
                "Denial-of-Wallet"
            ],
            "Vector and Embedding Weaknesses": [
                "Cross Context Leakage",
                "Embedding Leakage"
            ],
            "Improper Output Handling": [
                "Injection & Code Execution",
                "Web Output Vulnerabilities"
            ]
        }
    }
}

CYBERBENCH_TAXONOMY_DESCRIPTIVE = {
    "CyberBench": {
        "Sensitive Information Disclosure": {
            "Reconnaissance": [
                "Secrets Leakage""",
                "System Prompt Leakage",
                "Tool Enumeration"
            ],
            "IP": [
                "Trade Secret Leakage",
                "Patent Leakage",
                "Confidential Document Leakage"
            ],
            "PII": [
                "Cross Session Leakage",
                "Direct Leakage",
                "Database Leakage"
            ]
        },
        "System Behavior Abuse": {
            "Excessive Agency": [
                "Database",
                "Files",
                "Email",
                "Code",
                "Web"
            ],
            "Misinformation": [
                "Reputational Damage",
                "Hallucination",
                "Unauthorized Promises"
            ],
            "Unbounded Consumption": [
                "Denial of Service",
                "Denial of Wallet"
            ],
            "Vector and Embedding Weaknesses": [
                "Cross Context Leakage",
                "Embedding Leakage"
            ],
            "Improper Output Handling": [
                "Injection & Code Execution",
                "Web Output Vulnerabilities"
            ]
        }
    }
}

PROMPT_INJECTION_STRATEGIES = {
    "Instruction & Context Manipulation": [
        "ignore_previous_instructions",
        "persuasion",
        "system_mode",
        "virtualization",
        "indirect_reference",
    ],
    "Structural/Input Manipulation": [
        "payload_splitting",
        "repeated_token_attack",
        "overload_with_information"
    ],
    "Multilingual & Encoding Manipulation": [
        "output_formatting_manipulation",
        "token_smuggling",
        "different_user_input_language"
    ],
    "Algorithmic Mutations": [
        "Best-of-N"
    ]
}