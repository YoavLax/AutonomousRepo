// Tab Switching
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Initialize Chat functionality
    initChat();
    
    // Initialize Text Analysis
    initTextAnalysis();
    
    // Initialize Content Generator
    initContentGenerator();
});

// ============= CHAT FUNCTIONALITY =============
function initChat() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');

    // AI responses database
    const aiResponses = {
        greetings: [
            "Hello! How can I assist you today?",
            "Hi there! What would you like to know?",
            "Hey! I'm here to help. What's on your mind?"
        ],
        ai: [
            "Artificial Intelligence is fascinating! It's transforming how we interact with technology through machine learning, natural language processing, and computer vision.",
            "AI is revolutionizing various industries. From healthcare to finance, autonomous systems are becoming more sophisticated every day.",
            "The field of AI includes machine learning, deep learning, neural networks, and more. It's an exciting time to be exploring these technologies!"
        ],
        help: [
            "I can help you with various topics! Try asking me about AI, technology, or just have a conversation. You can also use the Text Analysis and Content Generator features.",
            "Feel free to ask me anything! I'm here to provide information and assistance. The tabs above offer additional tools for text analysis and content generation.",
            "I'm your AI assistant! Ask questions, explore ideas, or use the other features available in the tabs above."
        ],
        technology: [
            "Technology is evolving at an incredible pace! From quantum computing to blockchain, we're witnessing revolutionary innovations.",
            "The tech industry spans cloud computing, IoT, cybersecurity, and so much more. What specific area interests you?",
            "Modern technology is all about connectivity and intelligence. We're building smarter, more efficient systems every day."
        ],
        default: [
            "That's an interesting question! Could you tell me more about what you'd like to know?",
            "I appreciate your curiosity! Let me think about that...",
            "Great question! The answer depends on various factors. What aspect are you most interested in?",
            "I'm processing that query. In the meantime, feel free to explore the other features in the tabs above!",
            "Interesting topic! Based on current trends and developments, there's a lot to consider here."
        ]
    };

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';

        // Simulate AI thinking
        setTimeout(() => {
            const response = generateAIResponse(message);
            addMessage(response, 'assistant');
        }, 500 + Math.random() * 1000);
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = text;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function generateAIResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Check for keywords and return appropriate response
        if (lowerMessage.match(/\b(hi|hello|hey|greetings)\b/)) {
            return getRandomResponse(aiResponses.greetings);
        } else if (lowerMessage.match(/\b(ai|artificial intelligence|machine learning|neural|deep learning)\b/)) {
            return getRandomResponse(aiResponses.ai);
        } else if (lowerMessage.match(/\b(help|assist|support|guide)\b/)) {
            return getRandomResponse(aiResponses.help);
        } else if (lowerMessage.match(/\b(tech|technology|computer|software|code|programming)\b/)) {
            return getRandomResponse(aiResponses.technology);
        } else {
            return getRandomResponse(aiResponses.default);
        }
    }

    function getRandomResponse(responses) {
        return responses[Math.floor(Math.random() * responses.length)];
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// ============= TEXT ANALYSIS FUNCTIONALITY =============
function initTextAnalysis() {
    const analysisInput = document.getElementById('analysisInput');
    const analyzeButton = document.getElementById('analyzeButton');
    const analysisResults = document.getElementById('analysisResults');

    analyzeButton.addEventListener('click', () => {
        const text = analysisInput.value.trim();
        if (!text) {
            alert('Please enter some text to analyze!');
            return;
        }

        analyzeText(text);
        analysisResults.style.display = 'grid';
    });

    function analyzeText(text) {
        // Word count
        const words = text.match(/\b\w+\b/g) || [];
        const wordCount = words.length;
        document.getElementById('wordCount').textContent = wordCount.toLocaleString();

        // Character count
        const charCount = text.length;
        document.getElementById('charCount').textContent = charCount.toLocaleString();

        // Reading time (average 200 words per minute)
        const readTime = Math.ceil(wordCount / 200);
        document.getElementById('readTime').textContent = `${readTime} min`;

        // Paragraph count
        const paragraphs = text.split(/\n\n+/).filter(p => p.trim().length > 0);
        document.getElementById('paraCount').textContent = paragraphs.length;

        // Sentiment analysis (simple keyword-based)
        const sentiment = analyzeSentiment(text);
        document.getElementById('sentiment').textContent = sentiment;

        // Complexity (based on average word length)
        const avgWordLength = words.reduce((sum, word) => sum + word.length, 0) / wordCount;
        const complexity = avgWordLength < 4 ? 'Simple' : avgWordLength < 6 ? 'Moderate' : 'Complex';
        document.getElementById('complexity').textContent = complexity;
    }

    function analyzeSentiment(text) {
        const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'happy', 'best', 'awesome', 'brilliant', 'perfect'];
        const negativeWords = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor', 'disappointing', 'sad', 'angry', 'difficult'];
        
        const lowerText = text.toLowerCase();
        let positiveCount = 0;
        let negativeCount = 0;

        positiveWords.forEach(word => {
            const regex = new RegExp(`\\b${word}\\b`, 'g');
            positiveCount += (lowerText.match(regex) || []).length;
        });

        negativeWords.forEach(word => {
            const regex = new RegExp(`\\b${word}\\b`, 'g');
            negativeCount += (lowerText.match(regex) || []).length;
        });

        if (positiveCount > negativeCount * 1.5) return '😊 Positive';
        if (negativeCount > positiveCount * 1.5) return '😔 Negative';
        return '😐 Neutral';
    }
}

// ============= CONTENT GENERATOR FUNCTIONALITY =============
function initContentGenerator() {
    const generatorType = document.getElementById('generatorType');
    const generatorTopic = document.getElementById('generatorTopic');
    const generateButton = document.getElementById('generateButton');
    const generatedContent = document.getElementById('generatedContent');
    const generatedText = document.getElementById('generatedText');
    const copyButton = document.getElementById('copyButton');

    const templates = {
        headline: [
            "The Ultimate Guide to {topic}: Everything You Need to Know",
            "How {topic} is Revolutionizing the Industry in 2026",
            "10 Surprising Facts About {topic} That Will Blow Your Mind",
            "Why {topic} Matters More Than Ever in Today's World",
            "Mastering {topic}: A Comprehensive Approach for Beginners",
            "{topic}: The Future is Here and It's Incredible",
            "Breaking Down {topic}: Expert Insights and Analysis"
        ],
        paragraph: [
            "In today's rapidly evolving landscape, {topic} has emerged as a crucial element that shapes how we interact with the world. Experts agree that understanding {topic} is no longer optional—it's essential for anyone looking to stay ahead in their field. The implications are far-reaching, affecting everything from daily operations to long-term strategic planning.",
            "The world of {topic} is experiencing unprecedented growth and transformation. With new developments emerging constantly, it's an exciting time for enthusiasts and professionals alike. What makes {topic} particularly fascinating is its ability to adapt and evolve, constantly pushing the boundaries of what we thought possible.",
            "When exploring {topic}, it's important to consider both the practical applications and theoretical foundations. This multifaceted approach reveals not just the 'how' but also the 'why' behind {topic}. By understanding these deeper principles, we can better predict future trends and make more informed decisions."
        ],
        ideas: [
            "• Explore the intersection of {topic} and emerging technologies\n• Develop a comprehensive framework for implementing {topic}\n• Create educational content to democratize knowledge about {topic}\n• Build a community around {topic} enthusiasts and professionals\n• Research the historical evolution of {topic}\n• Analyze case studies of successful {topic} implementations\n• Design innovative solutions that leverage {topic}",
            "• Podcast series diving deep into {topic}\n• Interactive workshop on practical {topic} applications\n• Collaborative project bringing together {topic} experts\n• Blog documenting personal journey learning about {topic}\n• Video tutorials breaking down complex {topic} concepts\n• Research paper on the future of {topic}\n• Infographic visualizing key aspects of {topic}"
        ],
        summary: [
            "Summary of {topic}:\n\nKey Points:\n• {topic} represents a significant development in its field\n• Multiple approaches and methodologies exist\n• Growing interest and investment in this area\n• Practical applications span various industries\n• Continuous evolution and improvement\n\nConclusion: {topic} continues to be a vital area of focus with tremendous potential for growth and innovation.",
            "Executive Summary - {topic}:\n\nOverview: {topic} has become increasingly important in recent years, driving innovation and change across multiple sectors.\n\nCore Elements:\n- Foundational principles\n- Current implementations\n- Future possibilities\n- Challenges and opportunities\n\nOutlook: The trajectory for {topic} remains strongly positive, with expanding applications and continued development expected."
        ]
    };

    generateButton.addEventListener('click', () => {
        const topic = generatorTopic.value.trim();
        if (!topic) {
            alert('Please enter a topic or keywords!');
            return;
        }

        const type = generatorType.value;
        generateContent(type, topic);
    });

    function generateContent(type, topic) {
        const template = templates[type][Math.floor(Math.random() * templates[type].length)];
        const content = template.replace(/\{topic\}/g, topic);
        
        generatedText.textContent = content;
        generatedContent.style.display = 'block';
    }

    copyButton.addEventListener('click', () => {
        const text = generatedText.textContent;
        navigator.clipboard.writeText(text).then(() => {
            // Visual feedback
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyButton.style.background = '#10b981';
            
            setTimeout(() => {
                copyButton.innerHTML = originalText;
                copyButton.style.background = '';
            }, 2000);
        }).catch(err => {
            alert('Failed to copy text. Please try again.');
        });
    });
}

// Add some interactivity - typing effect for initial chat message
window.addEventListener('load', () => {
    console.log('AI Assistant Hub loaded successfully!');
    console.log('This application is autonomously developed by GitHub Copilot SDK Agent');
});
