from abc import ABC, abstractmethod
from typing import Dict, List, Type, Callable, Any
import asyncio
from dataclasses import dataclass

# ==================== BASE EVENT CLASS ====================
@dataclass
class Event:
    """Base event class that all specific events inherit from"""
    name: str
    data: Any = None

# ==================== INTERFACES ====================
class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: Event):
        """Publish an event to the event bus"""
        pass

class EventSubscriber(ABC):
    @abstractmethod
    async def handle(self, event: Event):
        """Handle an incoming event"""
        pass

    @abstractmethod
    def can_handle(self, event: Event) -> bool:
        """Check if this subscriber can handle the given event"""
        pass

# ==================== EVENT BUS ====================
class EventBus:
    def __init__(self):
        self._subscribers: Dict[Type[Event], List[EventSubscriber]] = {}
        self._filters: Dict[Type[Event], List[Callable[[Event], bool]]] = {}

    async def publish(self, event: Event):
        """Publish an event to all interested subscribers"""
        event_type = type(event)
        
        if event_type not in self._subscribers:
            return

        for subscriber in self._subscribers[event_type]:
            try:
                if self._should_handle(event, subscriber):
                    await subscriber.handle(event)
            except Exception as e:
                print(f"Error handling event {event.name}: {str(e)}")

    def subscribe(self, event_type: Type[Event], subscriber: EventSubscriber):
        """Subscribe a handler to a specific event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)

    def add_filter(self, event_type: Type[Event], filter_func: Callable[[Event], bool]):
        """Add a filter for specific event type"""
        if event_type not in self._filters:
            self._filters[event_type] = []
        self._filters[event_type].append(filter_func)

    def _should_handle(self, event: Event, subscriber: EventSubscriber) -> bool:
        """Check if an event should be handled based on filters and subscriber capability"""
        event_type = type(event)
        
        # Check subscriber's own capability first
        if not subscriber.can_handle(event):
            return False
        
        # Apply any registered filters
        if event_type in self._filters:
            return all(filter_func(event) for filter_func in self._filters[event_type])
        
        return True

# ==================== SAMPLE EVENTS ====================
class UserActionEvent(Event):
    """Event representing a user action"""
    pass

class SystemAlertEvent(Event):
    """Event representing a system alert"""
    pass

class DataChangeEvent(Event):
    """Event representing a data change"""
    pass

# ==================== SAMPLE HANDLERS ====================
class LoggingHandler(EventSubscriber):
    """Simple handler that logs all events"""
    async def handle(self, event: Event):
        print(f"[LOG] Event received: {event.name} - {event.data}")

    def can_handle(self, event: Event) -> bool:
        return True  # Handles all event types

class UserActionHandler(EventSubscriber):
    """Handler specifically for user actions"""
    async def handle(self, event: Event):
        print(f"Processing user action: {event.data}")

    def can_handle(self, event: Event) -> bool:
        return isinstance(event, UserActionEvent)

class AlertHandler(EventSubscriber):
    """Handler for system alerts"""
    async def handle(self, event: Event):
        print(f"ALERT: {event.data} - Taking action!")
        # Simulate some alert processing
        await asyncio.sleep(0.5)

    def can_handle(self, event: Event) -> bool:
        return isinstance(event, SystemAlertEvent)

# ==================== SAMPLE PUBLISHER ====================
class SystemEventPublisher(EventPublisher):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def publish(self, event: Event):
        print(f"Publishing event: {event.name}")
        await self.event_bus.publish(event)

# ==================== USAGE EXAMPLE ====================
async def main():
    # Create the event bus
    bus = EventBus()
    
    # Create publishers
    publisher = SystemEventPublisher(bus)
    
    # Create and register subscribers
    bus.subscribe(Event, LoggingHandler())  # Logs all events
    bus.subscribe(UserActionEvent, UserActionHandler())
    bus.subscribe(SystemAlertEvent, AlertHandler())
    
    # Add a filter - only handle alerts with priority > 3
    bus.add_filter(SystemAlertEvent, lambda e: e.data.get('priority', 0) > 3)
    
    # Publish some events
    await publisher.publish(UserActionEvent("login", {"username": "alice"}))
    await publisher.publish(SystemAlertEvent("cpu_high", {"priority": 5}))
    await publisher.publish(SystemAlertEvent("memory_low", {"priority": 2}))  # Will be filtered out
    await publisher.publish(DataChangeEvent("user_updated", {"id": 123}))

if __name__ == "__main__":
    asyncio.run(main())
