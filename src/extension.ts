/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';

import * as net from 'net';
import * as path from 'path';

import { workspace, Disposable, ExtensionContext, commands, window, debug } from 'vscode';
import { LanguageClient, LanguageClientOptions, SettingMonitor, ServerOptions, ErrorAction, ErrorHandler, CloseAction, TransportKind } from 'vscode-languageclient';

function startLangServer(command: string, args: string[], documentSelector: string[]): Disposable {
	const serverOptions: ServerOptions = {
		command,
		args,
		options: {
			cwd: path.join(__dirname, '..'),
			env: {
				PYTHONPATH: path.join(__dirname, '..')
			}
		}
	};
	const clientOptions: LanguageClientOptions = {
		documentSelector: documentSelector,
		synchronize: {
			configurationSection: "pyls"
		},
		outputChannelName: 'Behave'
	}
	return new LanguageClient(command, serverOptions, clientOptions).start();
}

// function startLangServerTCP(addr: number, documentSelector: string[]): Disposable {
// 	const serverOptions: ServerOptions = function() {
// 		return new Promise((resolve, reject) => {
// 			var client = new net.Socket();
// 			client.connect(addr, "127.0.0.1", function() {
// 				resolve({
// 					reader: client,
// 					writer: client
// 				});
// 			});
// 		});
// 	}

// 	const clientOptions: LanguageClientOptions = {
// 		documentSelector: documentSelector,
// 	}
// 	return new LanguageClient(`tcp lang server (port ${addr})`, serverOptions, clientOptions).start();
// }

export function activate(context: ExtensionContext) {
	context.subscriptions.push(startLangServer("/Users/donjayamanne/.local/share/virtualenvs/pythonVSCode-5rU-mS3t/bin/python", ["-m", "pyls", "-vv"], ["python", "feature"]));

	context.subscriptions.push(commands.registerCommand('behave.runscenario', (scenario: string) => {
		window.showInformationMessage(`Run Scenario: ${scenario}`);
	}))
	context.subscriptions.push(commands.registerCommand('behave.runfeature', (feature: string) => {
		window.showInformationMessage(`Run Feature: ${feature}`);
	}))
	context.subscriptions.push(commands.registerCommand('behave.runscenario_outline', (scenario: string) => {
		window.showInformationMessage(`Run Scenario Outline: ${scenario}`);
	}))
	context.subscriptions.push(commands.registerCommand('behave.debugscenario_outline', (feature: string) => {
		window.showInformationMessage(`Debug Scenario Outline: ${feature}`);
		startDebugging(feature);
	}))
	context.subscriptions.push(commands.registerCommand('behave.debugscenario', (scenario: string) => {
		window.showInformationMessage(`Debug Scenario: ${scenario}`);
		startDebugging(scenario);
	}))
	context.subscriptions.push(commands.registerCommand('behave.debugfeature', (feature: string) => {
		window.showInformationMessage(`Debug Feature: ${feature}`);
		startDebugging(feature);
	}))
	// For TCP server needs to be started seperately
	// context.subscriptions.push(startLangServerTCP(2087, ["python"]));
}

async function startDebugging(name?: string) {
	const pythonPath = '/Users/donjayamanne/.local/share/virtualenvs/pythonVSCode-5rU-mS3t/bin/python';
	const args = name ? ['-n', name] : [];
	const debugConfig = {
		name: 'Behave',
		type: 'python',
		request: 'launch',
		module: 'behave',
		pythonPath,
		args,
		// console: 'integratedTerminal'
		console: 'none'
	}
	await debug.startDebugging(workspace.workspaceFolders![0], debugConfig);
}
