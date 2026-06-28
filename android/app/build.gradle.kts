plugins {
    id("com.android.application")
}

android {
    namespace = "com.codemedi.cpx"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.codemedi.cpx"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
        buildConfigField("String", "CPX_SERVER_URL", "\"http://10.0.2.2:8787/\"")
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
