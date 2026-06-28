# Android Studio runner

Open this `android` directory as a project in Android Studio. Before running the
emulator, start the CPX service from the repository root:

```powershell
python -m cpx_agent.src.cpx_server --port 8787
```

The debug app loads `http://10.0.2.2:8787`, Android Emulator's alias for the
host machine. Physical devices require a reachable host address and a matching
`CPX_SERVER_URL` build configuration.

This wrapper intentionally contains no patient card, evaluator, or learner
profile data. Those remain in the Python service.

## Loading checks

If the emulator shows the loading or retry screen, verify the service before
restarting Android Studio:

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/health
```

The app retries one stalled main-frame load automatically and then exposes a
tap-to-retry error screen. Keep the service terminal open while using the app;
closing it makes both the WebView UI and the session API unavailable.
