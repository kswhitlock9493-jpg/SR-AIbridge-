import { useState, useEffect, useCallback, useContext, createContext } from 'react';
import { 
  getStatus, 
  getAgents, 
  getMissions, 
  getVaultLogs, 
  getCaptainMessages,
  getArmadaStatus,
  getFleetData,
  getActivity,
  getSystemHealthFull
} from '../api';
import { useWebSocket } from './useWebSocket';

/**
 * BridgeContext - Unified state management for SR-AIbridge
 * Provides centralized state for all components with real-time updates
 */
const BridgeContext = createContext();

/**
 * BridgeProvider - Context provider for the entire application
 */
export const BridgeProvider = ({ children }) => {
  // Core system state
  const [status, setStatus] = useState({
    agentsOnline: 0,
    activeMissions: 0,
    admiral: "Logged Out",
    systemHealth: 'unknown'
  });

  // Data states
  const [agents, setAgents] = useState([]);
  const [missions, setMissions] = useState([]);
  const [vaultLogs, setVaultLogs] = useState([]);
  const [captainMessages, setCaptainMessages] = useState([]);
  const [armadaStatus, setArmadaStatus] = useState({});
  const [fleetData, setFleetData] = useState([]);
  const [activity, setActivity] = useState([]);

  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);

  // Real-time states
  const [realTimeData, setRealTimeData] = useState({
    missions: [],
    vaultLogs: [],
    chatMessages: [],
    fleetData: []
  });

  // Guardian/System states
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [guardianActive, setGuardianActive] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);

  /**
   * Handle WebSocket messages for real-time updates
   */
  const handleWebSocketMessage = useCallback((message) => {
    console.log('📡 Bridge Real-time Update:', message.type);
    
    switch (message.type) {
      case 'mission_updated':
        setRealTimeData(prev => ({
          ...prev,
          missions: [...prev.missions, message.mission]
        }));
        // Also update missions state
        setMissions(prevMissions => {
          const existing = prevMissions.find(m => m.id === message.mission.id);
          if (existing) {
            return prevMissions.map(m => m.id === message.mission.id ? message.mission : m);
          }
          return [...prevMissions, message.mission];
        });
        break;
        
      case 'vault_log':
        setRealTimeData(prev => ({
          ...prev,
          vaultLogs: [message.log, ...prev.vaultLogs.slice(0, 49)]
        }));
        setVaultLogs(prev => [message.log, ...prev.slice(0, 49)]);
        break;
        
      case 'chat_message':
        setRealTimeData(prev => ({
          ...prev,
          chatMessages: [...prev.chatMessages, message.message]
        }));
        setCaptainMessages(prev => [...prev, message.message]);
        break;
        
      case 'fleet_update':
        setRealTimeData(prev => ({
          ...prev,
          fleetData: message.fleet
        }));
        setFleetData(message.fleet);
        break;
        
      case 'system_alert':
        setSystemAlerts(prev => [...prev, message.alert]);
        break;
        
      case 'guardian_activate':
        setGuardianActive(true);
        break;
        
      case 'status_update':
        setStatus(prev => ({ ...prev, ...message.status }));
        break;
        
      default:
        console.log('📡 Unhandled message type:', message.type);
    }
  }, []);

  // Initialize WebSocket connection
  const { 
    connected: wsConnected, 
    error: wsError, 
    send: wsSend 
  } = useWebSocket(handleWebSocketMessage);

  /**
   * Fetch all core data
   */
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [
        statusData,
        agentsData,
        missionsData,
        vaultLogsData,
        messagesData,
        armadaData,
        fleetDataResponse,
        activityData
      ] = await Promise.all([
        getStatus().catch(() => ({ 
          admiral: "Unknown", 
          agents_online: 0, 
          agentsOnline: 0, 
          active_missions: 0, 
          activeMissions: 0,
          fleet_count: 0,
          vault_logs: 0
        })),
        getAgents().catch(() => ({ agents: [], count: 0 })),
        getMissions().catch(() => ({ missions: [], count: 0 })),
        getVaultLogs().catch(() => []),
        getCaptainMessages().catch(() => []),
        getArmadaStatus().catch(() => ({})),
        getFleetData().catch(() => ({ fleet: [], count: 0, online: 0 })),
        getActivity().catch(() => [])
      ]);

      // Update status with new enhanced data structure
      setStatus(prev => ({
        ...prev,
        agentsOnline: statusData.agents_online ?? statusData.agentsOnline ?? 0,
        activeMissions: statusData.active_missions ?? statusData.activeMissions ?? 0,
        admiral: statusData.admiral ?? "Unknown",
        systemHealth: statusData.system_health ?? statusData.systemHealth ?? 'unknown'
      }));
      
      // Handle agents data structure (check if wrapped in response object)
      const agents = agentsData.agents || agentsData || [];
      setAgents(Array.isArray(agents) ? agents : []);
      
      // Handle missions data structure
      const missions = missionsData.missions || missionsData || [];
      setMissions(Array.isArray(missions) ? missions : []);
      
      // Handle vault logs
      setVaultLogs(Array.isArray(vaultLogsData) ? vaultLogsData : []);
      
      // Handle messages
      setCaptainMessages(Array.isArray(messagesData) ? messagesData : []);
      
      // Handle armada status
      setArmadaStatus(armadaData || {});
      
      // Handle fleet data structure
      const fleetData = fleetDataResponse.fleet || fleetDataResponse || [];
      setFleetData(Array.isArray(fleetData) ? fleetData : []);
      
      // Handle activity data structure
      const activities = activityData.activities || activityData || [];
      setActivity(Array.isArray(activities) ? activities : []);
      
    } catch (err) {
      console.error('Bridge data fetch failed:', err);
      setError(err.message || 'Failed to fetch bridge data');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Refresh specific data type
   */
  const refreshData = useCallback(async (dataType = 'all') => {
    try {
      switch (dataType) {
        case 'status':
          const statusData = await getStatus();
          setStatus(prev => ({
            ...prev,
            agentsOnline: statusData.agents_online ?? statusData.agentsOnline ?? 0,
            activeMissions: statusData.active_missions ?? statusData.activeMissions ?? 0,
            admiral: statusData.admiral ?? "Unknown"
          }));
          break;
        case 'agents':
          const agentsData = await getAgents();
          setAgents(agentsData);
          break;
        case 'missions':
          const missionsData = await getMissions();
          setMissions(missionsData);
          break;
        case 'vault':
          const vaultData = await getVaultLogs();
          setVaultLogs(vaultData);
          break;
        case 'messages':
          const messagesData = await getCaptainMessages();
          setCaptainMessages(messagesData);
          break;
        case 'armada':
          const armadaData = await getArmadaStatus();
          setArmadaStatus(armadaData);
          const fleetResponse = await getFleetData();
          setFleetData(fleetResponse);
          break;
        default:
          await fetchAllData();
      }
    } catch (err) {
      console.error(`Failed to refresh ${dataType}:`, err);
      setError(err.message || `Failed to refresh ${dataType}`);
    }
  }, [fetchAllData]);

  /**
   * System alert handler
   */
  const handleSystemAlert = useCallback((alert) => {
    setSystemAlerts(prev => [...prev, alert]);
  }, []);

  /**
   * Guardian activation handler
   */
  const handleGuardianActivate = useCallback((reason) => {
    setGuardianActive(true);
    console.log('🛡️ Guardian Mode activated via Bridge:', reason);
  }, []);

  /**
   * Fetch system health from /health/full endpoint
   */
  const fetchSystemHealth = useCallback(async () => {
    try {
      const healthData = await getSystemHealthFull();
      setSystemHealth(healthData);
      return healthData;
    } catch (err) {
      console.error('Failed to fetch system health:', err);
      setSystemHealth({
        status: 'error',
        error: err.message || 'Failed to fetch system health',
        components: {},
        self_heal_available: false
      });
      return null;
    }
  }, []);

  /**
   * Send WebSocket message
   */
  const sendMessage = useCallback((message) => {
    return wsSend(message);
  }, [wsSend]);

  // Initial data fetch on mount
  useEffect(() => {
    fetchAllData();
    
    // Set up periodic refresh every 30 seconds for critical data
    const interval = setInterval(() => {
      refreshData('status');
    }, 30000);
    
    return () => clearInterval(interval);
  }, [fetchAllData, refreshData]);

  // Update connection status
  useEffect(() => {
    setConnected(wsConnected);
  }, [wsConnected]);

  const contextValue = {
    // Data states
    status,
    agents,
    missions,
    vaultLogs,
    captainMessages,
    armadaStatus,
    fleetData,
    activity,
    realTimeData,
    
    // UI states
    loading,
    error,
    connected,
    wsError,
    
    // System states
    systemAlerts,
    guardianActive,
    systemHealth,
    
    // Actions
    refreshData,
    fetchAllData,
    fetchSystemHealth,
    handleSystemAlert,
    handleGuardianActivate,
    sendMessage,
    
    // Utilities
    clearError: () => setError(null),
    clearAlerts: () => setSystemAlerts([]),
    setGuardianActive
  };

  return (
    <BridgeContext.Provider value={contextValue}>
      {children}
    </BridgeContext.Provider>
  );
};

/**
 * useBridge hook - Access the unified bridge state
 */
export const useBridge = () => {
  const context = useContext(BridgeContext);
  if (!context) {
    throw new Error('useBridge must be used within a BridgeProvider');
  }
  return context;
};

export default useBridge;