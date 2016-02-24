from nltk.internals import java, config_java, find_jars_within_path
import re
import subprocess
import tempfile


class StanfordTagger:

    def __init__(self, model='stanford/models/english-bidirectional-distsim.tagger', libpath='stanford/'):
        self._model = model
        self._libs = find_jars_within_path(libpath)
        self._xml_regex = re.compile(
            r'  <word wid="[0-9]*" pos="([^"]*)" lemma="([^"]*)">(.*?)</word>')

        config_java(verbose=False)

    def tag(self, text, options=['-mx2g']):
        command = ['edu.stanford.nlp.tagger.maxent.MaxentTagger']
        command.extend(['-model', self._model])
        command.extend(['-outputFormat', 'xml'])
        command.extend(['-outputFormatOptions', 'lemmatize'])
        command.extend(options)

        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as text_file:
            text_file.write(text.encode('utf-8'))
            text_file.flush()

            command.extend(['-textFile', text_file.name])

            stdout, _ = java(command, classpath=self._libs,
                             stdout=subprocess.PIPE)
            output = stdout.decode('utf-8')

        tagged = []
        for line in output.splitlines():
            match = self._xml_regex.fullmatch(line)
            if match:
                tagged.append((match.group(3), match.group(2), match.group(1)))

        return tagged
