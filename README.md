# Q-SYS Plugin - Reflect Monitor Extension

## Overview

The **Reflect Monitor Extension Q-SYS Plugin** monitors selected controls on any Q-SYS component or plugin with Script Access and reports their state through a standard Q-SYS Monitoring Proxy.

It captures a baseline configuration, detects later value changes, updates the Monitoring Proxy status, and creates monitoring log entries with a configurable severity. This is useful for detecting configuration changes or unexpected state changes in components that do not provide the required monitoring behavior themselves.

## Features

- Discovers Q-SYS components and plugins with Script Access, including Monitoring Proxy components
- Monitors between 1 and 32 selected controls
- Displays the current value of every selected control
- Displays monitoring status and configuration errors in a status bar directly below the Monitoring Proxy selector
- Supports a user-friendly alias for each monitored control
- Captures and locks a baseline configuration
- Highlights values that differ from the locked baseline
- Reports changed values through a Q-SYS Monitoring Proxy
- Supports separate configurable compromised and back-to-normal log entries
- Offers `warning` and `error` severities for compromised entries; recovery entries use `normal`
- Passes through the selected component's `Status` state when available
- Saves the locked configuration and baseline on the Core

## Plugin Information

| Property | Value |
| --- | --- |
| Name | Reflect Monitor Extension |
| Version | 1.1.0 |
| Author | Jens Claerebout |

## Requirements

- Any Q-SYS component or plugin with Script Access and a unique Code Name
- A Q-SYS Monitoring Proxy with a unique Code Name and Script Access

The source component does not need a `Status` control. When one is present, its status is passed through to the Monitoring Proxy and takes priority over baseline-change reporting.

## Configuration

### Properties

| Property | Description |
| --- | --- |
| `Number of Controls` | Number of control rows to monitor (1-32) |
| `Reflect Ready` | Boolean, default `false`. Enable to write status directly to the selected component thas is Reflect Ready and does not need the Monitoring Proxy selector. |

### Plugin Controls

| Control | Description |
| --- | --- |
| `Component/Plugin` | Select any Q-SYS component or plugin with Script Access |
| `Monitoring Proxy` | Selects the Monitoring Proxy that receives status and log updates |
| `Lock Configuration` | Captures the current values as the baseline and prevents configuration changes |
| `Control` | Selects a control from the source component |
| `Alias` | Optional display name used in status messages and default log text |
| `Value` | Displays the current source-control value and is available as an output pin |
| `Compromised Log Entry` | Message sent once when the value differs from its locked baseline |
| `Back to Normal Log Entry` | Message sent once when a previously compromised value returns to baseline, with `normal` severity |
| `Severity` | Compromised log severity: `warning` (default) or `error` |
| `Status` | Displays the monitoring state and message, or a missing/unavailable proxy or status-update error |

Only the repeated `Value` controls are exposed as output pins. Configuration controls are available in the plugin UI.

## Behavior

### Component Discovery

The plugin discovers Q-SYS components and plugins with Script Access in the running design. Monitoring Proxy components are listed separately from other components and plugins. After selecting a source component, each `Control` row is populated with its available controls.

### Baseline and Locking

When `Lock Configuration` is enabled, the plugin records:

- the selected component and Monitoring Proxy
- the selected controls
- the current value of each selected control
- aliases, log messages, and severities

The component, proxy, control, alias, log-entry, and severity fields are disabled while locked. Unlock the configuration to make changes, then lock it again to capture a new baseline.

### Change Detection

While locked, a monitored value that differs from its baseline is highlighted in orange. The Monitoring Proxy receives a non-OK status containing the changed control and its previous and current values.

A compromised log entry is triggered once when a control first changes, using the selected `warning` or `error` severity. When that value returns to baseline, a back-to-normal log entry is triggered once with `normal` severity and the changed state is cleared. Repeated updates in either state do not create duplicate entries. Unlocking resets change tracking without generating recovery entries.

Both messages are editable per row and saved with the locked baseline. The default recovery message uses the alias or control name followed by "is back to normal." Older saved configurations remain readable; previously selected `normal` severities become `warning`.

### Source Status

If the selected source component has a control named `Status`, its numeric status and text are passed to the Monitoring Proxy. A non-OK source status takes priority over detected value changes. If the source has no `Status` control, its status is treated as OK.

### Reflect Ready Mode

With `Reflect Ready` disabled, the existing layout and external Monitoring Proxy behavior are retained. With it enabled, the status bar moves directly below the component selector and no external proxy is used. The selected component must expose a writable `Status` control (matched without regard to case). Missing or unwritable status controls are reported in the status bar.

Baseline changes update the component's own status. The extension ignores its own status events so its change warning can clear when values return to baseline. Independently reported component faults retain priority. The status control is excluded from selectable baseline controls in this mode to avoid monitoring the extension's own output.

Log entries are only supported through a Monitoring Proxy. Reflect Ready mode does not send log entries, and the compromised log entry, back-to-normal log entry, and severity fields are hidden. Status reporting and baseline-change detection remain active.

Reflect Ready baselines are stored separately using the selected component's Code Name; use one extension per target component. External-proxy mode retains its existing filenames.

### Persistence

The locked configuration and baseline are stored in a text file in the Core's `media` directory. The state filename is derived from the selected Monitoring Proxy Code Name so separate proxy instances can maintain separate state.

## Installation

1. Place `Reflect-Monitor-Extension.qplug` in the Q-SYS plugin directory or deploy it through Q-SYS Designer.
2. Add the plugin to the design.
3. Set `Number of Controls` to the required number of monitored controls.
4. Give the desired source component or plugin and Monitoring Proxy unique Code Names and enable Script Access.
5. Select any Q-SYS component or plugin with Script Access, then select the Monitoring Proxy.
6. Select the controls to monitor and optionally configure aliases, log messages, and severities.
7. Enable `Lock Configuration` to capture the baseline.
8. Deploy the design to the Q-SYS Core and verify the Monitoring Proxy status.

## Notes

- Changing the selected source component clears the configured control rows.
- The default log text is generated from the alias or control name and the value present when the control is selected.
- The Monitoring Proxy Code Name identifies the saved state and should remain unique and stable.
- Debug messages are enabled in version 1.1.0 and are written to the Q-SYS script log.

## Known Limitations

- Control comparison is text-based, so formatting changes can be reported as value changes.
- Component and control discovery occurs when the plugin script starts or when the source selection changes.

## Changelog

### 1.1.0

- Made the UI approximately 20% smaller with compact fields, status bars, spacing, and text in both monitoring modes.
- Added separate compromised and back-to-normal log messages per control, with one recovery log entry when a changed value returns to baseline.
- Limited selectable compromised severity to `warning` and `error`; recovery entries use `normal` severity.
- Updated saved baselines to include recovery messages while retaining support for older state files.
- Added a status bar below the Monitoring Proxy selector to display monitoring status, baseline changes, source faults, and configuration errors.
- Added the `Reflect Ready` boolean property, defaulting to `false` to retain the existing external Monitoring Proxy behavior.
- In Reflect Ready mode, hid the Monitoring Proxy selector and moved the status bar below the component selector.
- Added direct updates to the selected component's writable `Status` control, with handling to ignore the extension's own status events.
- Limited log entries to Monitoring Proxy mode and hid log-entry and severity fields in Reflect Ready mode.
- Added separate baseline storage keyed by the component's Code Name for Reflect Ready mode.

### 1.0.0

- Initial plugin release with discovery of Q-SYS components and plugins with Script Access and 1-32 monitored control rows.
- Added baseline capture and configuration locking, live value display, and highlighting of changed values.
- Added aliases, configurable log messages and severities, and status reporting through an external Monitoring Proxy.
- Added source-status passthrough and persistent storage of the locked configuration and baseline on the Core.

## License

MIT License

## Author

Jens Claerebout
