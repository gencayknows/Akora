**Akura**

*Akura is a minimalist, modern, and lightning-fast cross-platform music player.*

- **Known Issues**

Real-time Timeline Progress Bar UI Sync (Open Issue)

Status: Open / Help Wanted

*The playback timeline slider and current time counter do not continuously re-render second-by-second during active playback on certain Python/Flet desktop thread runtimes. The state updates internally upon manual user interactions (e.g., toggling play/pause or seeking), but background thread UI ticker updates fail to trigger continuous visually smooth slider movement.*

Contributions: I'm open to pull requests addressing thread-safe control re-rendering or event loop scheduling in Flet.
