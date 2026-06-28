package com.codemedi.cpx;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.ConsoleMessage;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.TextView;

public final class MainActivity extends Activity {
    private static final String TAG = "CodeMediCpx";
    private static final long LOAD_TIMEOUT_MS = 8_000L;

    private WebView webView;
    private TextView loadingStatus;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private boolean pageFinished;
    private boolean retryEnabled;
    private int loadAttempt;

    private final Runnable loadTimeout = () -> {
        if (pageFinished || webView == null) return;
        if (loadAttempt < 2) {
            loadAttempt += 1;
            webView.stopLoading();
            webView.loadUrl(BuildConfig.CPX_SERVER_URL);
            return;
        }
        webView.stopLoading();
        showLoadProblem("CPX 화면을 불러오지 못했습니다.\n서버 실행 상태를 확인한 뒤 눌러서 다시 시도하세요.");
    };

    @Override
    @SuppressLint("SetJavaScriptEnabled")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(85, 53, 36));
        webView.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        loadingStatus = new TextView(this);
        loadingStatus.setGravity(Gravity.CENTER);
        loadingStatus.setTextColor(Color.rgb(255, 246, 223));
        loadingStatus.setTextSize(16);
        loadingStatus.setBackgroundColor(Color.rgb(85, 53, 36));
        loadingStatus.setPadding(40, 40, 40, 40);
        loadingStatus.setOnClickListener(view -> {
            if (retryEnabled) loadApp();
        });

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);

        if (BuildConfig.DEBUG) WebView.setWebContentsDebuggingEnabled(true);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                pageFinished = false;
                showLoading();
                scheduleLoadTimeout();
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                pageFinished = true;
                mainHandler.removeCallbacks(loadTimeout);
                loadingStatus.setVisibility(View.GONE);
            }

            @Override
            public void onReceivedError(
                    WebView view,
                    WebResourceRequest request,
                    WebResourceError error
            ) {
                if (!request.isForMainFrame()) return;
                mainHandler.removeCallbacks(loadTimeout);
                showLoadProblem("CPX 서버에 연결할 수 없습니다.\n서버를 실행한 뒤 눌러서 다시 시도하세요.");
            }

            @Override
            public void onReceivedHttpError(
                    WebView view,
                    WebResourceRequest request,
                    WebResourceResponse errorResponse
            ) {
                if (!request.isForMainFrame()) return;
                mainHandler.removeCallbacks(loadTimeout);
                showLoadProblem("CPX 서버 응답 오류 (" + errorResponse.getStatusCode()
                        + ")\n눌러서 다시 시도하세요.");
            }
        });
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage message) {
                Log.d(TAG, message.message() + " @" + message.lineNumber());
                return true;
            }
        });

        FrameLayout root = new FrameLayout(this);
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        root.addView(loadingStatus, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        if (savedInstanceState == null) {
            loadApp();
        } else if (webView.restoreState(savedInstanceState) == null) {
            loadApp();
        } else {
            showLoading();
            scheduleLoadTimeout();
        }
    }

    private void loadApp() {
        loadAttempt = 1;
        pageFinished = false;
        showLoading();
        scheduleLoadTimeout();
        webView.stopLoading();
        webView.loadUrl(BuildConfig.CPX_SERVER_URL);
    }

    private void showLoading() {
        retryEnabled = false;
        loadingStatus.setText("CPX 화면을 불러오는 중…");
        loadingStatus.setVisibility(View.VISIBLE);
    }

    private void showLoadProblem(String message) {
        pageFinished = false;
        retryEnabled = true;
        loadingStatus.setText(message);
        loadingStatus.setVisibility(View.VISIBLE);
    }

    private void scheduleLoadTimeout() {
        mainHandler.removeCallbacks(loadTimeout);
        mainHandler.postDelayed(loadTimeout, LOAD_TIMEOUT_MS);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
            return;
        }
        super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        mainHandler.removeCallbacks(loadTimeout);
        webView.loadUrl("about:blank");
        webView.destroy();
        webView = null;
        super.onDestroy();
    }
}
