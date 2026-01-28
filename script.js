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

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';

        // Show "AI is typing..." indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing';
        typingDiv.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content"><em>AI is typing...</em></div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            // Remove typing indicator
            chatMessages.removeChild(typingDiv);
            if (data.response) {
                addMessage(data.response, 'assistant');
            } else if (data.error) {
                addMessage("Error: " + data.error, 'assistant');
            } else {
                addMessage("Sorry, I didn't understand that.", 'assistant');
            }
        } catch (err) {
            chatMessages.removeChild(typingDiv);
            addMessage("Network error. Please try again.", 'assistant');
        }
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

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// ============= TEXT ANALYSIS FUNCTIONALITY =============
function initTextAnalysis() {
    // ... (unchanged)
}

// ============= CONTENT GENERATOR FUNCTIONALITY =============
function initContentGenerator() {
    // ... (unchanged)
}

// Add some interactivity - typing effect for initial chat message
window.addEventListener('load', () => {
    console.log('AI Assistant Hub loaded successfully!');
    console.log('This application is autonomously developed by GitHub Copilot SDK Agent');
});
This change upgrades the chat to use real AI responses from your backend, making the feature truly useful and impressive.