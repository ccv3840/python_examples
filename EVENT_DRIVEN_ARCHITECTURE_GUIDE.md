# Event-Driven Architecture: Complete Learning Guide

## 🎯 What is Event-Driven Architecture?

**Simple Definition:**
Instead of modules calling each other directly, they communicate by **emitting events** that others can **listen to**.

**Analogy: Newspaper Publishing**
```
❌ OLD WAY (Direct Communication):
  Reader calls Publisher: "Do you have news?"
  Publisher calls Reader: "Here's your news"
  Reader calls Printer: "Print this"
  Printer calls Reader: "Printed!"
  Everyone is busy calling each other

✅ NEW WAY (Event-Driven):
  Publisher: "I have news!" (emits event)
  ↓
  Everyone listening gets notified automatically
  Reader gets news, Printer gets news, Advertiser gets news
  No one calls each other, everyone reacts independently
```

---

## 🏗️ Core Concepts

### 1. **Event** - Something that happened

```python
@dataclass
class Event:
    """Represents something that happened in the system."""
    event_type: str        # WHAT happened? (e.g., "user_logged_in")
    source: str            # WHO emitted this? (e.g., "AuthModule")
    timestamp: datetime    # WHEN did it happen?
    data: dict            # WHAT data? (e.g., {'user_id': 123})

# Examples
user_login_event = Event(
    event_type='user_logged_in',
    source='AuthModule',
    timestamp=datetime.now(),
    data={'user_id': 123, 'username': 'alice'}
)

order_created_event = Event(
    event_type='order_created',
    source='OrderModule',
    timestamp=datetime.now(),
    data={'order_id': 456, 'total': 99.99}
)
```

### 2. **Emitter** - Broadcasts events

```python
class AuthModule:
    """Emits authentication events."""
    
    def login(self, username: str, password: str, event_bus):
        # ... validate credentials ...
        
        # EMIT event instead of calling other modules
        event_bus.emit(Event(
            event_type='user_logged_in',
            source='AuthModule',
            timestamp=datetime.now(),
            data={'username': username}
        ))
        print(f"✅ Emitted: user_logged_in")
```

### 3. **Listener/Subscriber** - Reacts to events

```python
class NotificationModule:
    """Listens for events and reacts."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        
        # Subscribe to events
        self.event_bus.subscribe('user_logged_in', self.on_user_login)
        self.event_bus.subscribe('order_created', self.on_order_created)
    
    def on_user_login(self, event: Event):
        """Called when user logs in."""
        username = event.data['username']
        print(f"📨 Sending welcome email to {username}")
    
    def on_order_created(self, event: Event):
        """Called when order is created."""
        order_id = event.data['order_id']
        print(f"📨 Sending order confirmation for #{order_id}")
```

### 4. **Event Bus** - Central hub for events

```python
class EventBus:
    """Central event dispatcher - the heart of event-driven architecture."""
    
    def __init__(self):
        self.subscribers = {}  # event_type → list of callbacks
    
    def subscribe(self, event_type: str, callback):
        """Register to listen for an event."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"🎧 Subscribed to '{event_type}'")
    
    def emit(self, event: Event):
        """Broadcast event to all listeners."""
        print(f"📢 Event emitted: {event.event_type} from {event.source}")
        
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                callback(event)  # Call all listeners
```

---

## 🎬 Real-World Analogy: Coffee Shop

**Without Event-Driven (Direct Calls):**
```
1. You: "Barista, make coffee!"
2. Barista: "Ok, I'm making coffee"
3. Barista to Cashier: "Coffee is done, charge customer"
4. Cashier to You: "That'll be $5"
5. You to Barista: "Here's $5"
6. Barista to Cashier: "Payment received"
7. Cashier to You: "Receipt is printing"
8. Printer to Cashier: "Receipt done"

Everyone is constantly calling each other!
```

**With Event-Driven:**
```
1. You: Order coffee (emit event: "coffee_ordered")

2. Barista hears event:
   → Makes coffee
   → When done, emits: "coffee_ready"

3. Cashier hears event "coffee_ordered":
   → Charges you
   → Emits: "payment_requested"

4. You hear event "payment_requested":
   → Pay
   → Emit: "payment_received"

5. Printer hears event "payment_received":
   → Prints receipt
   → Emit: "receipt_printed"

Everyone does their job independently!
No one needs to call anyone else!
```

---

## 🔧 Simple Example: Step-by-Step

### Step 1: Create Event Bus
```python
event_bus = EventBus()  # Central hub
```

### Step 2: Create Event
```python
event = Event(
    event_type='button_clicked',
    source='UI',
    timestamp=datetime.now(),
    data={'button_name': 'Submit'}
)
```

### Step 3: Create Listeners
```python
def handle_button_click(event: Event):
    print(f"Handler 1: Button clicked! {event.data['button_name']}")

def log_event(event: Event):
    print(f"Handler 2: Logging event {event.event_type}")

# Register listeners
event_bus.subscribe('button_clicked', handle_button_click)
event_bus.subscribe('button_clicked', log_event)
```

### Step 4: Emit Event
```python
event_bus.emit(event)
```

### Output
```
🎧 Subscribed to 'button_clicked'
🎧 Subscribed to 'button_clicked'
📢 Event emitted: button_clicked from UI
Handler 1: Button clicked! Submit
Handler 2: Logging event button_clicked
```

**Notice:**
- ✅ The button doesn't call the handlers directly
- ✅ Multiple handlers can react to the same event
- ✅ New handlers can be added without changing the button
- ✅ Handlers don't know about each other

---

## 💻 Complete Working Example

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Dict

# ===== EVENT =====
@dataclass
class Event:
    event_type: str
    source: str
    timestamp: datetime
    data: dict

# ===== EVENT BUS =====
class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """Listen for an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"🎧 {callback.__self__.__class__.__name__} subscribed to '{event_type}'")
    
    def emit(self, event: Event):
        """Broadcast event to all listeners."""
        print(f"\n📢 [{event.source}] Event: {event.event_type}")
        print(f"   Data: {event.data}")
        
        if event.event_type not in self.subscribers:
            print("   No subscribers")
            return
        
        # Call all listeners
        for callback in self.subscribers[event.event_type]:
            callback(event)

# ===== MODULES =====

class UserModule:
    """Handles user actions."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    def login(self, username: str):
        """User logs in - emit event."""
        self.event_bus.emit(Event(
            event_type='user_logged_in',
            source='UserModule',
            timestamp=datetime.now(),
            data={'username': username}
        ))
    
    def logout(self, username: str):
        """User logs out - emit event."""
        self.event_bus.emit(Event(
            event_type='user_logged_out',
            source='UserModule',
            timestamp=datetime.now(),
            data={'username': username}
        ))

class NotificationModule:
    """Sends notifications when events happen."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Listen for events
        self.event_bus.subscribe('user_logged_in', self.on_login)
        self.event_bus.subscribe('user_logged_out', self.on_logout)
    
    def on_login(self, event: Event):
        username = event.data['username']
        print(f"   📧 NotificationModule: Sending welcome email to {username}")
    
    def on_logout(self, event: Event):
        username = event.data['username']
        print(f"   🔔 NotificationModule: Sending goodbye notification to {username}")

class AnalyticsModule:
    """Tracks user actions."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Listen for events
        self.event_bus.subscribe('user_logged_in', self.track_login)
        self.event_bus.subscribe('user_logged_out', self.track_logout)
    
    def track_login(self, event: Event):
        username = event.data['username']
        print(f"   📊 AnalyticsModule: Logged login event for {username}")
    
    def track_logout(self, event: Event):
        username = event.data['username']
        print(f"   📊 AnalyticsModule: Logged logout event for {username}")

class SecurityModule:
    """Monitors security events."""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Listen for events
        self.event_bus.subscribe('user_logged_in', self.log_access)
    
    def log_access(self, event: Event):
        username = event.data['username']
        print(f"   🔒 SecurityModule: Access logged for {username}")

# ===== USAGE =====

if __name__ == '__main__':
    print("="*70)
    print("EVENT-DRIVEN ARCHITECTURE EXAMPLE")
    print("="*70)
    
    # Create event bus
    event_bus = EventBus()
    
    # Create modules
    user_module = UserModule(event_bus)
    notification_module = NotificationModule(event_bus)
    analytics_module = AnalyticsModule(event_bus)
    security_module = SecurityModule(event_bus)
    
    print("\n" + "="*70)
    print("USER LOGS IN")
    print("="*70)
    
    # User logs in - this emits an event
    user_module.login('alice')
    
    print("\n" + "="*70)
    print("USER LOGS OUT")
    print("="*70)
    
    # User logs out - this emits an event
    user_module.logout('alice')
    
    print("\n" + "="*70)
    print("KEY INSIGHT: UserModule didn't call other modules!")
    print("Other modules listened and reacted independently!")
    print("="*70)
```

**Output:**
```
======================================================================
EVENT-DRIVEN ARCHITECTURE EXAMPLE
======================================================================

🎧 NotificationModule subscribed to 'user_logged_in'
🎧 NotificationModule subscribed to 'user_logged_out'
🎧 AnalyticsModule subscribed to 'user_logged_in'
🎧 AnalyticsModule subscribed to 'user_logged_out'
🎧 SecurityModule subscribed to 'user_logged_in'

======================================================================
USER LOGS IN
======================================================================

📢 [UserModule] Event: user_logged_in
   Data: {'username': 'alice'}
   📧 NotificationModule: Sending welcome email to alice
   📊 AnalyticsModule: Logged login event for alice
   🔒 SecurityModule: Access logged for alice

======================================================================
USER LOGS OUT
======================================================================

📢 [UserModule] Event: user_logged_out
   Data: {'username': 'alice'}
   🔔 NotificationModule: Sending goodbye notification to alice
   📊 AnalyticsModule: Logged logout event for alice

======================================================================
KEY INSIGHT: UserModule didn't call other modules!
Other modules listened and reacted independently!
======================================================================
```

---

## 🎓 Key Principles of Event-Driven Architecture

### 1. **Decoupling**
```python
# ❌ OLD: Tight coupling
class UserModule:
    def __init__(self, notification_module, analytics_module):
        self.notification_module = notification_module
        self.analytics_module = analytics_module
    
    def login(self, username):
        self.notification_module.send_email()  # Direct call
        self.analytics_module.track()          # Direct call

# ✅ NEW: Loose coupling
class UserModule:
    def __init__(self, event_bus):
        self.event_bus = event_bus
    
    def login(self, username):
        self.event_bus.emit(Event(...))  # Only emits, doesn't care who listens
```

### 2. **Modularity**
Each module does ONE job:
- UserModule: Manages users
- NotificationModule: Sends notifications
- AnalyticsModule: Tracks events
- SecurityModule: Logs access

No module knows about others!

### 3. **Extensibility**
Add new features without modifying existing code:
```python
class EmailModule:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe('user_logged_in', self.send_email)

# Just add this module - no changes needed to UserModule!
email_module = EmailModule(event_bus)
```

### 4. **Testability**
Test each module independently:
```python
def test_notification_on_login():
    event_bus = EventBus()
    notification = NotificationModule(event_bus)
    
    # Emit event directly
    event = Event(event_type='user_logged_in', ...)
    event_bus.emit(event)
    
    # Check notification was sent
    assert notification.emails_sent > 0
```

---

## 📊 Event Types (Naming Conventions)

Use clear, past-tense names for events (something already happened):

```python
# ✅ GOOD (past tense - something happened)
'user_logged_in'
'order_created'
'payment_processed'
'email_sent'
'file_uploaded'

# ❌ BAD (present/future tense - commands)
'login_user'
'create_order'
'process_payment'
'send_email'
```

---

## 🔄 Event Flow Pattern

```
1. Something happens
   ↓
2. Module A emits event
   ↓
3. Event Bus receives event
   ↓
4. Event Bus finds all subscribers
   ↓
5. Event Bus calls each subscriber
   ↓
6. Subscribers react independently
```

Example flow:
```
User clicks "Buy Now" button
   ↓
OrderModule emits 'order_created'
   ↓
EventBus receives 'order_created'
   ↓
EventBus finds subscribers:
   - PaymentModule
   - NotificationModule
   - AnalyticsModule
   - InventoryModule
   ↓
Each module reacts:
   PaymentModule: "I'll charge the card"
   NotificationModule: "I'll send confirmation"
   AnalyticsModule: "I'll log this sale"
   InventoryModule: "I'll update stock"
```

---

## ✅ Pros and Cons

### ✅ Advantages

```
✅ Loose coupling (modules don't know each other)
✅ Easy to add new features (just add new listeners)
✅ Easy to test (test each module independently)
✅ Scalable (can handle many events)
✅ Reactive (modules respond automatically)
✅ Auditable (can log all events)
✅ Extensible (new modules without changing existing)
```

### ❌ Disadvantages

```
❌ Complexity (more code, harder to understand initially)
❌ Debugging harder (hard to trace event flow)
❌ Performance (slight overhead for event dispatch)
❌ Event hell (too many events can be confusing)
```

---

## 🎯 When to Use Event-Driven Architecture

### ✅ Use when:
```
- Multiple modules need to react to the same action
- You want to decouple modules
- You need to add features without modifying existing code
- You have complex workflows with many steps
- You need audit trail / event logging
- You want reactive systems (things respond automatically)
```

### ❌ Don't use when:
```
- Simple, small applications
- Few modules with direct dependencies
- Performance is critical (events have overhead)
- Hard real-time systems (events aren't deterministic)
```

---

## 🔗 Event-Driven Patterns

### Pattern 1: Request/Response with Events

```python
# A needs something from B
class ModuleA:
    def request_data(self):
        self.event_bus.emit(Event(
            event_type='data_requested',
            source='ModuleA',
            data={'request_id': 123}
        ))

class ModuleB:
    def on_data_requested(self, event):
        # Process request
        response_data = self.get_data()
        
        # Send response as event
        self.event_bus.emit(Event(
            event_type='data_response',
            source='ModuleB',
            data={'request_id': event.data['request_id'], 'response': response_data}
        ))

class ModuleA:
    def on_data_response(self, event):
        # Got response!
        print(f"Received response: {event.data['response']}")
```

### Pattern 2: Saga Pattern (Multi-Step Process)

```python
# Step 1: Order created
'order_created'
    ↓
# Step 2: Payment Module listens
'payment_processed'
    ↓
# Step 3: Inventory Module listens
'inventory_reserved'
    ↓
# Step 4: Shipping Module listens
'shipment_created'
    ↓
# Step 5: Notification Module listens
'order_ready_for_shipping'
```

### Pattern 3: CQRS (Command Query Responsibility Segregation)

```python
# Commands (things that change state)
'order_placed'
'payment_charged'
'stock_decreased'

# Queries (things that read state)
'get_order_status'
'get_inventory'
```

---

## 🎯 Your Multi-Module Problem Solved with Events

Remember your question: "ClassB modifies var1, how does ClassA know?"

**With Event-Driven Architecture:**

```python
class ModuleB:
    def process(self, var1_from_a: str):
        # Process something
        modified = var1_from_a.upper()
        
        # DON'T modify var1
        # Instead, EMIT event requesting change
        self.event_bus.emit(Event(
            event_type='var1_change_requested',
            source='ModuleB',
            data={'new_value': modified, 'reason': 'processing complete'}
        ))

class ModuleA:
    def __init__(self, event_bus):
        self.var1 = 'original'
        self.event_bus = event_bus
        
        # Listen for change requests
        self.event_bus.subscribe('var1_change_requested', self.on_var1_change_request)
    
    def on_var1_change_request(self, event):
        """A decides if B's suggestion is valid."""
        new_value = event.data['new_value']
        reason = event.data['reason']
        
        if self._validate(new_value):
            self.var1 = new_value
            print(f"✅ ClassA accepted change from {event.source}: {reason}")
            
            # Announce the change
            self.event_bus.emit(Event(
                event_type='var1_changed',
                source='ModuleA',
                data={'new_value': new_value}
            ))
        else:
            print(f"❌ ClassA rejected change from {event.source}")
```

**Benefits:**
- ✅ ClassB doesn't directly modify var1
- ✅ ClassA explicitly validates changes
- ✅ Audit trail shows who requested what change
- ✅ Other modules (ClassC) can react to changes
- ✅ Fully traceable!

---

## 📝 Summary

**Event-Driven Architecture** is:
1. Modules communicate via **events** (messages about things that happened)
2. Modules **emit** events when something important happens
3. Other modules **listen** for events they care about
4. Central **Event Bus** coordinates communication
5. No module calls another directly

**Key Benefit:** Loose coupling + Easy to extend + Fully traceable

This is a professional pattern used in:
- Microservices
- Real-time systems
- Reactive applications
- Message-driven architectures

Start simple, add complexity as needed! 🎯

