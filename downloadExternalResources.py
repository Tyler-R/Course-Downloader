from bs4 import BeautifulSoup
import requests
import mimetypes
import wget
import os
import webbrowser
import urllib

# configuration options
modifySourceFile = True
downloadFilesWithExtensions = True
downloadFilesWithoutExtensions = True
manuallyDownloadIgnoredFiles = False
viewIgnoredLinks = True

htmlFilePath = ''
htmlFile = open(htmlFilePath, 'r');
htmlFileDirectory = os.sep.join(htmlFilePath.split(os.sep)[0: -1])

ignoredLinks = []

soup = BeautifulSoup(htmlFile, 'lxml')
htmlFile.close()
extensions = ('.pdf', '.ppt', '.zip', '.pptx', '.dat', '.mp4', '.mp3')

defaultDownloadDirectoryName = "external resources"
defaultDownloadDirectoryPath = htmlFileDirectory + os.sep + defaultDownloadDirectoryName + os.sep

failedToDownloadList = []

numberOfDownloadedLinks = 0

def download(link, extension=''):
    global numberOfDownloadedLinks
    print('downloading: ', link['href'])
    try:
        filePath = wget.download(link['href'], out=defaultDownloadDirectoryPath)
    except urllib.error.HTTPError:
        print("HTTP ERROR OCCURED\n\n")
        failedToDownloadList.append(link)
        return
    # extract fileName from path and then strip '/' and '\' from path
    fileName = filePath.split('/')[-1].split('\\')[-1]
    link['href'] = defaultDownloadDirectoryName + os.sep + fileName
    print('saved file to: ', link['href'])
    numberOfDownloadedLinks += 1

    if extension != '' and not fileName.endswith(extension):
        oldFilePath = htmlFileDirectory + os.sep + defaultDownloadDirectoryName + os.sep + fileName
        newFilePath = oldFilePath + extension
        os.rename(oldFilePath, newFilePath)

        link['href'] = link['href'] + extension
        print("adding extension by changing file name/path to: ", newFilePath)

# make default directory if it does not exist to put downloaded files into
if not os.path.exists(defaultDownloadDirectoryPath):
    os.makedirs(defaultDownloadDirectoryPath)

totalLinks = soup.find_all('a')

for link in totalLinks:
    if link.get('href', '').startswith('http'): # link to external website / resource
        # print(str(link['href']))
        if link['href'].endswith(extensions): # link ends in file extension
            if downloadFilesWithExtensions:
                download(link)

        elif(not link['href'].endswith('/')): # link does not end in file extension and is not a directory path
            try:
                response = requests.head(link['href'], timeout=2.0, allow_redirects=True)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                failedToDownloadList.append(link)
                print("READING HTTP HEADER ERROR OCCURED\n\n")
                break
            content_type = response.headers['content-type']
            extension = mimetypes.guess_extension(content_type)

            if downloadFilesWithoutExtensions:
                if response.url != link['href']:
                    print("link was redirected:")
                    print("changing '" + link['href'] + "'   ----->   ' " + response.url)
                    link['href'] = response.url

                if extension in extensions:
                    if link['href'].endswith(extension):
                        download(link)
                    else:
                        download(link, extension)

            if extension not in extensions:
                ignoredLinks.append(link)
                print("ignoring link with unsupported extension: ", extension, " - ", link['href'])

        else: # link ends in directory path
            ignoredLinks.append(link)
            print("ignoring link that ends with '/': ", link['href'])

print("\n\n")

print("the following links were ignored:")
for link in ignoredLinks:
    print(link['href'])

print("\n\n")

if viewIgnoredLinks:
    for link in ignoredLinks:
        webbrowser.open_new_tab(link['href'])

"""
if manuallyDownloadIgnoredFiles:
    for link in ignoredLinks:
        webbrowser.open_new_tab(link['href'])
        choice = input('Ignore this link? (y/n)')
        if choice == 'n':
            newUrl = input('Enter a new URL or leave blank to continue')
            if newUrl != '':
                download(link)
        else:
            print("did not download: ", link['href'])
"""

for link in failedToDownloadList:
    print ("could not download: ", link['href'])

print("\n\n-----------------------Summary-----------------------")

print(str(len(totalLinks)) + "\tlinks were found in the html file.")
print(str(len(failedToDownloadList)) + "\tlinks were not downloaded.")
print(str(len(ignoredLinks)) + "\tlinks were ignored.")
print(str(numberOfDownloadedLinks) + "\tlinks were downloaded")

if modifySourceFile:
    print("modifying source html file")
    os.rename(htmlFilePath, htmlFilePath + '.backup')
    htmlFile = open(htmlFilePath, 'w');
    htmlFile.write(soup.prettify())
    htmlFile.close()

""" just have wget do the request to the server.
for link in soup.find_all('a'):
    if not link['href'].startswith('http'):
        # print(str(link['href']))
        folders = link['href'].split('/')
        for i in range(len(folders) - 1):
            print(folders[i])
"""
