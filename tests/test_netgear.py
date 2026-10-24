"""Run with a Python environment containing lupa (Lua runtime)."""
from pathlib import Path
from lupa import LuaRuntime

source = (Path(__file__).resolve().parents[1] / 'Reflect-Monitor-Extension.qplug').read_text()
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(source)  # Compile entire plugin; design functions remain available.
lua.execute('''
props = {}
for _, property in ipairs(GetProperties()) do props[property.Name] = property end
RectifyProperties(props)
assert(props['Switch Port'].IsHidden)
props['Netgear AV Switch'].Value = true
RectifyProperties(props)
assert(not props['Switch Port'].IsHidden)
local layout = GetControlLayout(props)
assert(layout.ResetSwitchPort and layout.NetgearSwitch)
props['Netgear AV Switch'].Value = false
assert(GetControlLayout(props).ResetSwitchPort == nil)
props['Netgear AV Switch'].Value = true
Properties = props
runtimeControls = { NetgearSwitch = {String='switch'}, Component={String='source'},
  Status={}, ResetSwitchPort={} }
Timer = {New=function() return {Start=function(self, seconds) self.seconds=seconds; self.running=true end,
  Stop=function(self) self.running=false end} end}
poe = {Boolean=true}; port = {Boolean=true}
Component = {New=function() return {['EnablePoE 1']=poe, ['EnablePort 1']=port} end,
 GetControls=function() return {} end}
sourceComponent = {}; sourceStatus = {Value=2}; reflectReady=false
function controlValue(control) return control and control.Value end
function evaluateMonitoring()
  runtimeControls.Status.Value = netgearConfigurationError and 1 or 0
  runtimeControls.Status.String = netgearConfigurationError or 'OK'
end
logs={}
function sendMonitorLog(message, severity) table.insert(logs, {message, severity}) end
''')
block = source[source.index('-- Keep timers referenced'):source.index('function discoverComponents()')]
lua.execute(block)
lua.execute('''
runtimeControls.NetgearSwitch.String=''
pollPortReset()
assert(runtimeControls.Status.String == 'Select a Netgear AV Switch')
runtimeControls.NetgearSwitch.String='switch'
runtimeControls.NetgearSwitch.EventHandler()
assert(runtimeControls.Status.String == 'OK' and netgearConfigurationError == nil)
pollPortReset()
assert(portFaultTimer.running and portFaultTimer.seconds == 300)
sourceStatus.Value=0; pollPortReset()
assert(not portFaultTimer.running and not portFaultPending)
sourceStatus.Value=2; pollPortReset(); portFaultTimer.EventHandler()
assert(not poe.Boolean and not port.Boolean and portRestoreTimer.seconds==5)
assert(runtimeControls.ResetSwitchPort.IsDisabled and logs[1][2]=='warning')
runtimeControls.NetgearSwitch.String='other'
portRestoreTimer.EventHandler()
assert(poe.Boolean and port.Boolean and not runtimeControls.ResetSwitchPort.IsDisabled)
pollPortReset(); portFaultTimer.EventHandler(); portRestoreTimer.EventHandler()
pollPortReset(); assert(not portFaultPending) -- One reset per continuous episode.
sourceStatus.Value=0; pollPortReset()
runtimeControls.ResetSwitchPort.EventHandler()
assert(portResetActive and not port.Boolean)
portRestoreTimer.EventHandler()
assert(port.Boolean and poe.Boolean)
Component.New=function() return {} end
pollPortReset()
assert(runtimeControls.Status.String:find('write access', 1, true))
Component.New=function() return {['EnablePoE 1']=poe, ['EnablePort 1']=port} end
Component.GetControls=function() return {{Name='EnablePoE 1', Direction='Read Only'}} end
assert(netgearControls()==nil)
Component.GetControls=function() return {} end
-- Restore the second control even if the first restore raises.
local broken=setmetatable({}, {__newindex=function() error('write failure') end})
portRestoreControls={broken, port}; port.Boolean=false
portRestoreTimer.EventHandler()
assert(port.Boolean and runtimeControls.Status.String:find('restore failed',1,true))
''')
print('PASS: Lua compilation, properties/layout, cancellation, automatic/manual reset, deduplication, validation, partial restoration')
