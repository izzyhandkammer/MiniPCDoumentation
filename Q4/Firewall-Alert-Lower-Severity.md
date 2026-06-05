# Firewall Alert Exclusions
1. make sure your xdr instance is in the same TSG as your firewall
2. Settings → Datasources and Integrations → Add New → NGFW
3. Allow it to take a while to connect
4. Now you should be ingesting raw logs from the firewall (check via XQL search `dataset = panw_ngfw_traffic_raw` )
5. Create Automation Rule
	- Name: `High Severity FW Threat`
	- Conditions: `Action = Prevented (Blocked) AND Severity = High, Critical`
6. Playbook settings:
	- Name: Lower Severity Blocked FW Alerts
	- Triggers: High Severity FW Threat
7. Conditional Block: Was the threat blocked?
	* Condition for Yes: Get: `issue.alert_action_status` Equals Get `BLOCKED`
8. Yes -> Standard Task: update-issue
	* Scripts: `core-update-issue (Cortex Core - Platform)`
	* Inputs:
		* id: `${issue.id}`
		* severity: `low`
		* status: Resolved - `Known Issue`
9. Test the playbook by downloading [sample malware](https://docs.paloaltonetworks.com/advanced-wildfire/administration/configure-advanced-wildfire-analysis/verify-wildfire-submissions/test-a-sample-malware-file)
