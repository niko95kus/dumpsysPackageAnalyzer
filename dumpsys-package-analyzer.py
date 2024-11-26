#!/usr/bin/env python3

import csv
import re
import argparse

result = []

def main():
	parser = argparse.ArgumentParser(description="Analyze Android dumpsys package output", usage=argparse.SUPPRESS)
	parser.add_argument("-i", "--input", required=True, help="dumpsys package output file")
	parser.add_argument("-o", "--output", required=True, help="CSV output filename")

	try:
		args = parser.parse_args()
	except:
		print()
		parser.print_help()
		exit()

	inputFile = args.input
	outputFile = args.output

	global result
	packageCount = 0
	firstInstallTime = lastUpdateTime = originatingPackageName = initiatingPackageName = installerPackageName = tmp = ''

	with open(inputFile, 'r') as file:
		isOnPackagesSection = False # flag to check if current line is in the 'Packages' section of dumpsys output

		for line in file:
			if 'Package [' in line:
				packageCount += 1

				# write result before processing next package
				if packageCount > 1:
					writeResult(packageName, firstInstallTime, lastUpdateTime, originatingPackageName, initiatingPackageName, installerPackageName)
					
					# reset variables
					firstInstallTime = lastUpdateTime = originatingPackageName = initiatingPackageName = installerPackageName = tmp = ''

				isOnPackagesSection = True

				package = re.search('\[\S*\]', line)

				# get package name
				if package is not None:
					package = package.group()

					package = re.sub('\[', '', package)
					packageName = re.sub('\]', '', package)
					
					print('Processing {}'.format(packageName))
				else:
					print(line)
			elif isOnPackagesSection:
				# Get data
				line = line.strip()

				if 'lastUpdateTime' in line:
					lastUpdateTime = parseResult(line)
				elif 'firstInstallTime' in line:
					firstInstallTime = parseResult(line)
				elif 'installerPackageName' in line:
					installerPackageName = parseResult(line)
				elif 'initiatingPackageName' in line:
					initiatingPackageName = parseResult(line)
				elif 'originatingPackageName' in line:
					originatingPackageName = parseResult(line)
						
			elif 'Queries:' in line: 
				# end of 'Packages' section
				writeResult(firstInstallTime, lastUpdateTime, originatingPackageName, initiatingPackageName, installerPackageName)
				break

	if packageCount > 0:
		with open(outputFile, 'w') as csvfile:
			fields = ['packageName', 'firstInstallTime', 'lastUpdateTime', 'originatingPackageName', 'initiatingPackageName', 'installerPackageName']

			writer = csv.DictWriter(csvfile, fieldnames=fields, lineterminator='\n')
			writer.writeheader()
			writer.writerows(result)

		print()
		print('Processed {} package(s)'.format(packageCount))
		print('Result written to {}'.format(outputFile))
	else:
		print("Cannot find packages list. Exiting...")

def writeResult(packageName, firstInstallTime, lastUpdateTime, originatingPackageName, initiatingPackageName, installerPackageName):
	global result
	tmp = {'packageName':packageName, 'firstInstallTime': firstInstallTime, 'lastUpdateTime': lastUpdateTime, 'originatingPackageName': originatingPackageName, 'initiatingPackageName': initiatingPackageName, 'installerPackageName': installerPackageName}

	result.append(tmp)

def parseResult(str):
	tmp = (str.strip()).split("=")
	return tmp[1]



if __name__ == "__main__":
    main()