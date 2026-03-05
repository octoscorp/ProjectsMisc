import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log("Hello world activated");

    const disposable = vscode.commands.registerCommand('extension.helloWorld', () => {
        vscode.window.showInformationMessage('Hello World!');
    });

    context.subscriptions.push(disposable);
}