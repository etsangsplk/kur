"""
Copyright 2017 Deepgram

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import numpy
from . import EvaluationHook

logger = logging.getLogger(__name__)

###############################################################################
class Transcript:
	""" Container for holding transcripts.
	"""

	###########################################################################
	def __init__(self, transcript):
		self.transcript = transcript

	###########################################################################
	def __str__(self):
		return self.transcript

	###########################################################################
	def __repr__(self):
		return '{}({})'.format(self.__class__.__name__, self.transcript)

###############################################################################
class TranscriptHook(EvaluationHook):
	""" Post-evaluation hook for speech data, which prints sample transcripts
	using argmax decoding
	"""

	###########################################################################
	@classmethod
	def get_name(cls):
		""" Returns the name of the evaluation hook.
		"""
		return 'transcript'

	###########################################################################
	@staticmethod
	def argmax_decode(output, rev_vocab, blank, separator):
		""" output = matrix: timesteps * characters
		"""
		x = numpy.argmax(output, axis=1)
		tokens = []
		prev = None
		for c in x:
			if c == prev:
				continue
			if c != blank:
				tokens.append(c)
			prev = c
		offset = 1 if blank == 0 else 0
		return separator.join([rev_vocab[i-offset] for i in tokens])

	###########################################################################
	def __init__(self, word=False, warp=False, **kwargs):
		""" Creates a new transcript hook.
		"""

		super().__init__(**kwargs)
		self.warp = warp
		self.word = word

	###########################################################################
	def apply(self, current, original, model=None):
		""" Applies the hook to the data.
		"""

		data, truth = current
		if data is None or 'asr' not in data or len(data['asr']) == 0:
			logger.warning('Transcript hook called without any data.')
			return data

		has_truth = truth is not None and \
			'transcript_raw' in truth and \
			len(truth['transcript_raw']) > 1

		k = model.provider.keys.index('transcript_raw')
		vocab = model.provider.sources[k].vocab
		rev = {v : k for k, v in vocab.items()}

		blank = len(vocab) if not self.warp else 0

		separator = ' ' if self.word else ''

		prediction = data['asr'][0]
		result = {
			'prediction' : Transcript(self.argmax_decode(
				prediction,
				rev,
				blank,
				separator
			)),
			'truth' : Transcript(separator.join(
				rev.get(i, '') for i in truth['transcript_raw'][0]
			)) if has_truth else None
		}
		print('Prediction: "{}"'.format(result['prediction']))
		if has_truth:
			print('Truth: "{}"'.format(result['truth']))

		return (result['prediction'], result['truth'])

#### EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF
