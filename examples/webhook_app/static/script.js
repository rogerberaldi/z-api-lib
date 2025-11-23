const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
const ws = new WebSocket(wsUrl);

const eventFeed = document.getElementById('event-feed');
const eventTemplate = document.getElementById('event-template');
const wsStatus = document.getElementById('ws-status');
const eventCountEl = document.getElementById('event-count');
const lastEventTimeEl = document.getElementById('last-event-time');
const connectionStatusEl = document.getElementById('connection-status');
const clearBtn = document.getElementById('clear-btn');

let eventCount = 0;

ws.onopen = () => {
    wsStatus.classList.add('connected');
    console.log('WebSocket Connected');
};

ws.onclose = () => {
    wsStatus.classList.remove('connected');
    console.log('WebSocket Disconnected');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleEvent(data);
};

clearBtn.addEventListener('click', () => {
    eventFeed.innerHTML = '<div class="empty-state"><p>Feed cleared</p></div>';
    eventCount = 0;
    eventCountEl.textContent = '0';
});

function handleEvent(data) {
    // Remove empty state if present
    const emptyState = eventFeed.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    // Update stats
    eventCount++;
    eventCountEl.textContent = eventCount;
    lastEventTimeEl.textContent = new Date().toLocaleTimeString();

    // Update connection status indicator if applicable
    if (data.type === 'INSTANCE_CONNECTED') {
        updateConnectionStatus(true);
    } else if (data.type === 'INSTANCE_DISCONNECTED') {
        updateConnectionStatus(false);
    }

    // Create event card
    const clone = eventTemplate.content.cloneNode(true);
    const card = clone.querySelector('.event-card');

    // Set type badge
    const badge = card.querySelector('.event-type-badge');
    badge.textContent = data.type.replace(/_/g, ' ');
    badge.classList.add(`type-${data.type}`);

    // Set time
    const timeEl = card.querySelector('.event-time');
    timeEl.textContent = new Date().toLocaleTimeString();

    // Set summary
    const summaryEl = card.querySelector('.event-summary');
    summaryEl.textContent = getEventSummary(data);

    // Set payload
    const payloadEl = card.querySelector('.event-payload code');
    payloadEl.textContent = JSON.stringify(data.payload, null, 2);

    // Prepend to feed
    eventFeed.insertBefore(card, eventFeed.firstChild);
}

function updateConnectionStatus(connected) {
    const dot = connectionStatusEl.querySelector('.dot');
    const text = connectionStatusEl.querySelector('.text');

    if (connected) {
        dot.classList.remove('disconnected');
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        dot.classList.add('disconnected');
        text.textContent = 'Disconnected';
    }
}

function getEventSummary(data) {
    const p = data.payload;

    switch (data.type) {
        case 'RECEIVED_MESSAGE':
            const sender = p.senderName || p.phone;
            if (p.text) return `Text from ${sender}: "${p.text.message}"`;
            if (p.image) return `Image from ${sender}`;
            if (p.audio) return `Audio from ${sender}`;
            if (p.video) return `Video from ${sender}`;
            if (p.document) return `Document from ${sender}`;
            return `Message from ${sender}`;

        case 'SENT_MESSAGE':
            return `Message sent to ${p.phone}`;

        case 'MESSAGE_STATUS':
            return `Message ${p.id} status: ${p.status}`;

        case 'INSTANCE_CONNECTED':
            return `Instance ${p.instanceId} connected`;

        case 'INSTANCE_DISCONNECTED':
            return `Instance disconnected`;

        case 'CHAT_PRESENCE':
            return `${p.phone} is ${p.presence}`;

        default:
            return 'Unknown Event';
    }
}
