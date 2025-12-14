/**
 * CommandDeckV1 - Heritage Bridge Command Deck
 * Restored nostalgic CRT-style deck mode with real-time event streaming
 */

import { useBridgeStream } from "../hooks/useBridgeStream";
import TaskStatusCard from "../components/DeckPanels/TaskStatusCard";
import AgentMetricsTable from "../components/DeckPanels/AgentMetricsTable";
import AnomalyFeed from "../components/DeckPanels/AnomalyFeed";
import FaultControls from "../components/DeckPanels/FaultControls";
import DemoLaunchPad from "../components/DeckPanels/DemoLaunchPad";
import EventStreamTap from "../components/DeckPanels/EventStreamTap";
import "../styles/deck.css";

export default function CommandDeckV1() {
  const { events, metrics, send } = useBridgeStream();

  return (
    <div className="deck-root crt">
      <header className="deck-header">
        <h1>🌉 SR-AIbridge • Command Deck</h1>
        <div className="badges">
          <span className="badge badge-blue">MAS</span>
          <span className="badge badge-gold">Autonomy</span>
          <span className="badge badge-green">Cascade</span>
          <span className="badge badge-red">Fault/Heal</span>
        </div>
      </header>
      
      <section className="deck-grid">
        <TaskStatusCard metrics={metrics} />
        <AgentMetricsTable metrics={metrics} />
        <AnomalyFeed events={events} />
        <EventStreamTap events={events} />
        <FaultControls onInject={(cfg) => send({ type: "fault.config", cfg })} />
        <DemoLaunchPad onStart={(mode) => send({ type: "demo.start", mode })} />
      </section>
    </div>
  );
}
