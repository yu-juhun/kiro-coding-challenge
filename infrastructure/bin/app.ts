#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { EventManagementStack } from '../lib/event-management-stack';

const app = new cdk.App();
new EventManagementStack(app, 'EventManagementStack');
