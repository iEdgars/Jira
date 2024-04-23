import pandas as pd
import streamlit as st

cacheTime = 900

def typeEmoji(type):
    if str(type) == 'Story':
        emoji = '📝'
    elif str(type) == 'Bug':
        emoji = '🐛'
    elif str(type) == 'Spike':
        emoji = '📌' #'🌵'
    elif str(type) == 'Epic':
        emoji = '🚀'
    else:
        emoji = ''

    return emoji

@st.cache_data(ttl=cacheTime)
def blockedStories(_jiraConnection, project, component, server):
    columns = ['Item number', 'Link', 'Subject', 'Assignee', 'Reporter', 'Type', 'TypeEmoji', 'Epic', 'Epic link', 'Epic Status']
    df = pd.DataFrame(columns=columns)

    status = 'Blocked'
    blockingStatuses = ['Ready','Blocked','Backlog','In Progress','UAT', 'In Testing', 'Ready for Refinement', 'IN DEFINITION', 'Technical Review']
    nonBlockingStatuses = ['Done','Rejected']

    query = f'project = {project} AND component = {component} AND status = {status}'

    startAt = 0
    issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)
    linkedIssues = issues

    while len(issues) > 0:
        # for issue in issues:
            # print(issue.key, issue.fields.summary, issue.fields.status, issue.fields.assignee, issue.fields.created[:10], issue.fields.updated[:10], issue.fields.updated[11:16], issue.permalink())
        startAt += 50
        issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)
        linkedIssues.extend(issues)

    theIssues = []
    parents = []

    for item in linkedIssues:
        blockedIssues = [link for link in item.fields.issuelinks if link.type.name == 'Blocks']

        activeBlockers = []
        for bi in blockedIssues:
            if hasattr(bi, 'inwardIssue'):
                if bi.inwardIssue.fields.status.name in blockingStatuses:
                    activeBlockers.append(f'{bi.inwardIssue.key} [{bi.inwardIssue.fields.status}]')
                    # print(f'Blocked By: {bi.inwardIssue.key}, {bi.inwardIssue.fields.status}')
        
        try:
            parentEpic = item.fields.parent
            parentStatus = str(parentEpic.fields.status)
            epicLink = f'{server}/browse/{str(item.fields.parent)}'
        except:
            parentEpic = 'No Parent'
            parentStatus = None
            epicLink = None

        emoji = typeEmoji(item.fields.issuetype)

        if len(activeBlockers) == 0:

            ticket = [item.key, item.permalink(), item.fields.summary, item.fields.assignee, item.fields.reporter, item.fields.issuetype, emoji, parentEpic, epicLink, parentStatus]
            df.loc[len(df)] = ticket
        
        else:
            pass
    
    df = df.drop_duplicates()

    return df

cacheTime = 900
@st.cache_data(ttl=cacheTime)
def storiesToBlock(_jiraConnection, project, component, server):
    columns = ['Item number', 'Link', 'Subject', 'Assignee', 'Reporter', 'Type', 'TypeEmoji', 'Epic', 'Epic link']
    df = pd.DataFrame(columns=columns)

    status = 'Ready'
    blockingStatuses = ['Ready','Blocked','Backlog','In Progress','UAT', 'In Testing', 'Ready for Refinement', 'IN DEFINITION']
    nonBlockingStatuses = ['Done','Rejected']

    query = f'project = {project} AND component = {component} AND status = {status}'

    startAt = 0
    issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)
    linkedIssues = issues

    while len(issues) > 0:
        # for issue in issues:
            # print(issue.key, issue.fields.summary, issue.fields.status, issue.fields.assignee, issue.fields.created[:10], issue.fields.updated[:10], issue.fields.updated[11:16], issue.permalink())
        startAt += 50
        issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)
        linkedIssues.extend(issues)

    theIssues = []
    parents = []

    for item in linkedIssues:
        blockedIssues = [link for link in item.fields.issuelinks if link.type.name == 'Blocks']

        activeBlockers = []
        for bi in blockedIssues:
            if hasattr(bi, 'inwardIssue'):
                if bi.inwardIssue.fields.status.name in blockingStatuses:
                    activeBlockers.append(f'{bi.inwardIssue.key} [{bi.inwardIssue.fields.status}]')
                    # print(f'Blocked By: {bi.inwardIssue.key}, {bi.inwardIssue.fields.status}')
        
        try:
            parentEpic = item.fields.parent
            epicLink = f'{server}/browse/{str(item.fields.parent)}'
        except:
            parentEpic = 'No Parent'
            epicLink = ''

        emoji = typeEmoji(item.fields.issuetype)

        if len(activeBlockers) != 0:

            ticket = [item.key, item.permalink(), item.fields.summary, item.fields.assignee, item.fields.reporter, item.fields.issuetype, emoji, parentEpic, epicLink]
            df.loc[len(df)] = ticket
        
        else:
            pass
    
    df = df.drop_duplicates()

    return df

@st.cache_data(ttl=900)
def blockedEpics(_jiraConnection, project):
    columns = ['Item number', 'Link', 'Subject', 'Assignee', 'Reporter', 'Type', 'TypeEmoji', 'Epic', 'Epic link', 'Epic Subject', 'Status', 'Team']
    df = pd.DataFrame(columns=columns)

    status = 'Blocked'
    query = f'project = {project} and status = {status} and type = Epic ORDER BY updated DESC, created DESC'

    startAt = 0
    issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)

    while len(issues) > 0:
        for issue in issues:
            child_stories = _jiraConnection.search_issues(f'"Epic Link" = {issue.key}')
            for story in child_stories:
                for component in story.fields.components:
                    if str(component) in ['DA','DE']:
                        emoji = typeEmoji(story.fields.issuetype)
                        ticket = [story.key, story.permalink(), story.fields.summary, story.fields.assignee, story.fields.reporter, story.fields.issuetype, emoji, issue.key, issue.permalink(), issue.fields.summary, str(story.fields.status), str(component)]
                        df.loc[len(df)] = ticket

        startAt += 50
        issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)

    return df

@st.cache_data(ttl=cacheTime)
def readyForRefinementItems(_jiraConnection, project, component, server, status):
    columns = ['Item number', 'Link', 'Subject', 'Assignee', 'Reporter', 'Type', 'Priority', 'TypeEmoji', 'Epic', 'Epic link', 'DATA: Work type']
    df = pd.DataFrame(columns=columns)

    # query = f'project = {project} AND component = {component} AND status = "{status}" AND type in (Bug, Story) ORDER BY cf[10011] ASC'
    query = f'project = {project} AND component = {component} AND status = "{status}" AND type NOT IN (Epic) ORDER BY cf[10011] ASC'

    startAt = 0
    issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)

    while len(issues) > 0:
    # while startAt < 100:
        for issue in issues:

            try:
                parentEpic = issue.fields.parent
                epicLink = f'{server}/browse/{str(issue.fields.parent)}'
            except:
                parentEpic = 'No Parent'
                epicLink = ''

            try:
                if str(getattr(issue.fields, 'customfield_10366')) == 'None':
                    dataWorkType = f"{getattr(issue.fields, 'customfield_10366')} "
                else:
                    dataWorkType = getattr(issue.fields, 'customfield_10366')
            except:
                dataWorkType = 'No DATA Worktype'

            emoji = typeEmoji(issue.fields.issuetype)

            ticket = [issue.key, issue.permalink(), issue.fields.summary, issue.fields.assignee, issue.fields.reporter, 
                      issue.fields.issuetype, str(issue.fields.priority)[:2], emoji, parentEpic, epicLink, dataWorkType]
            df.loc[len(df)] = ticket
            
        startAt += 50
        issues = _jiraConnection.search_issues(query, startAt=startAt, maxResults=50)

    return df