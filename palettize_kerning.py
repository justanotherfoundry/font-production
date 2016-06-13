# -*- coding: utf-8 -*-

import fontTools.ttLib


# Reduces the number of different kerning values in the font,
# similar to a GIF or PNG-8 color palette.

# This is lossy but should be nearly imperceptible.
# The aim is to allow for better compression in webfonts and reduce the webfont file size.

# font is a fontTools.ttLib.TTFont object
# max_tweak_relative defines the maximum any kern value may be changed (relative to the UPM)
def palettize_kerning( font, max_tweak_relative = 0.003 ):
	max_tweak = max_tweak_relative * font['head'].unitsPerEm
	if max_tweak < 1:
		return
	# collect and delete valueRecords
	allValueRecords = []
	try:
		featureList = font['GPOS'].table.FeatureList
	except KeyError:
		return
	lookups = font['GPOS'].table.LookupList.Lookup
	for feature_indx in range( len( featureList.FeatureRecord ) ):
		if featureList.FeatureRecord[feature_indx].FeatureTag == 'kern':
			feat = featureList.FeatureRecord[feature_indx].Feature
			for lookup_indx in range( feat.LookupCount ):
				lookupListIndex = feat.LookupListIndex[lookup_indx]
				for subtable_indx in range( len( lookups[lookupListIndex].SubTable ) -1, -1, -1 ):
					subtable = lookups[lookupListIndex].SubTable[subtable_indx]
					if subtable.Format == 1:
						for pset_index in range( len( subtable.PairSet ) -1, -1, -1 ):
							pairSet = subtable.PairSet[pset_index]
							for pv_index in range( len( pairSet.PairValueRecord ) -1, -1, -1 ):
								valueRecord = pairSet.PairValueRecord[pv_index].Value1
								if abs( valueRecord.XAdvance ) > max_tweak:
									allValueRecords.append( valueRecord )
								else:
									del pairSet.PairValueRecord[pv_index]
					else:
						for class1_index in range( subtable.Class1Count -1, -1, -1 ):
							class1Record = subtable.Class1Record[class1_index]
							for class2_index in range( subtable.Class2Count -1, -1, -1 ):
								valueRecord = class1Record.Class2Record[class2_index].Value1
								if abs( valueRecord.XAdvance ) > max_tweak:
									allValueRecords.append( valueRecord )
								else:
									valueRecord.XAdvance = 0
					# TODO: delete unused classes
				# TODO: would sorting the kerning values lead to further improvements in compression?
	# create sorted unique list of all kerning values
	allValues = list( { valueRecord.XAdvance for valueRecord in allValueRecords } )
	allValues.sort()
	# set up spans
	spans = []
	max_span = int( round( 2.0 * max_tweak + 1 ) )
	lower = allValues[0]
	for v in allValues:
		if v < lower + max_span:
			upper = v
		else:
			spans.append( [ int( lower ), int( upper ) ] )
			lower = v
			upper = v
	spans.append( [ int( lower ), int( upper ) ] )
	# equalize adjacent spans
	for i in xrange( len( spans ) - 1 ):
		# middle of the outer limits of the two spans
		middle = ( spans[i][0] + spans[i+1][1] ) // 2 # always rounds down
		if spans[i][1] > middle:
			# spans[i] is shortened
			spans[i][1] = middle
			# spans[i] might be shortened further if there are empty slots
			while spans[i][1] > spans[i][0] and spans[i][1] not in allValues:
				spans[i][1] -= 1
			# spans[i+1] is extended
			spans[i+1][0] = middle + 1
			# spans[i+1] might be shortened
			while spans[i+1][0] < spans[i+1][1] and spans[i+1][0] not in allValues:
				spans[i+1][0] += 1
		else:
			# we know that spans[i+1] is never extended
			assert( spans[i+1][0] >= middle + 1 )
	# set up the mapping
	mapping = {}
	for span in spans:
		middle = int( 0.5 * ( span[0] + span[1] ) ) # always rounds towards zero
		for i in range( span[0], span[1] + 1 ):
			mapping[i] = middle
	# apply the actual palettization
	for valueRecord in allValueRecords:
		valueRecord.XAdvance = mapping[valueRecord.XAdvance]

# usage example
font = fontTools.ttLib.TTFont( 'source.ttf' )
palettize_kerning( font )
font.save( 'palettized.ttf' )
