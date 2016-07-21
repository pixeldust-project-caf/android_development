/*
 * Copyright (C) 2016 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.example.android.pushapithirdpartytwo;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.accounts.AccountManagerCallback;
import android.accounts.AccountManagerFuture;
import android.accounts.AuthenticatorDescription;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

/**
 * A minimal "Hello, World!" application.
 */
public class MainActivity extends Activity {
    /**
     * Called with the activity is first created.
     */
    private static AccountManager am;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        am = AccountManager.get(getApplicationContext());
        final TextView loginTypesRegistered = (TextView) findViewById(R.id.logintypesregistered2);
        final TextView visibleAccounts = (TextView) findViewById(R.id.visibleaccounts2);
        final Button getVisibleAccounts = (Button) findViewById(R.id.getvisibleaccounts2);
        final Toast notifOn = Toast.makeText(getApplicationContext(), "Notifs Turned On!",
                Toast.LENGTH_SHORT);
        final Toast notifOff = Toast.makeText(getApplicationContext(), "Notifs Turned Off!",
                Toast.LENGTH_SHORT);
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage("Welcome to Test App 1.\nPlease make sure you have:\n\n1. Test App 1\n"
                + "\n2. Auth App \n\ninstalled for the demo. These applications together provide" +
                " tests, use cases, and proof of concept of Push API!\n")
                .setTitle("WELCOME")
                .setPositiveButton("Okay", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialogInterface, int i) {
                //do nothing
            }
        });
        AlertDialog dialog = builder.create();
        dialog.show();
        String supportedPackages = "";
        try{
            ApplicationInfo ai = getPackageManager().getApplicationInfo(getPackageName(),
                    PackageManager.GET_META_DATA);
            Bundle bundle = ai.metaData;
            supportedPackages = bundle.getString("android.accounts.SupportedLoginTypes");
        } catch (PackageManager.NameNotFoundException e) {
            Log.e("PushApiTestAppTwo", "Failed to load meta-data, NameNotFound: "
                    + e.getMessage());
        } catch (NullPointerException e) {
            Log.e("PushApiTestAppTwo", "Failed to load meta-data, NullPointer: " + e.getMessage());
        }
        String[] manifestSupportedAccountTypes = supportedPackages.split(";");
        final StringBuilder masterString = new StringBuilder();
        for (int i = 0 ; i < manifestSupportedAccountTypes.length ; i++) {
            masterString.append(manifestSupportedAccountTypes[i] + "\n");
        }
        if (masterString.length() > 0) {
            loginTypesRegistered.setText(masterString);
        }
        else {
            loginTypesRegistered.setText("----");
        }
        getVisibleAccounts.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Account[] accountsAccessedByAuthApp = am.getAccounts();
                StringBuilder masterString = new StringBuilder();
                for (int i = 0 ; i < accountsAccessedByAuthApp.length ; i++) {
                    masterString.append(accountsAccessedByAuthApp[i].name + ", " +
                            accountsAccessedByAuthApp[i].type + "\n");
                }
                if (masterString.length() > 0) {
                    visibleAccounts.setText(masterString);
                }
                else {
                    visibleAccounts.setText("----");
                }
            }
        });
    }
}