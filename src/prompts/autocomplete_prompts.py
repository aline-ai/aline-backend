# map_prompt = """
# <article>
# {content}
# </article>

# <notes>
# {notes}
# </notes>
# Relevant text verbatim, if any:
# """

map_prompt = """\n\nHuman: Use the following portion of a long article to see if any of the text is relevant complete the incomplete notes. COPY any relevant text VERBATIM, meaning word-for-word.
<article>
{content}
</article>

<notes>
{notes}
</notes>
Relevant text verbatim, if any:
\n\nAssistant:
"""

reduce_prompt = """\n\nHuman:
<summaries>
{summaries}
</summaries>

The following are a small section of notes written according to the following:
* The notes are based on the context, *not* on prior knowledge
    * An answer will *not* be written if the answer is not found in the long article
    * Nothing will be written if nothing is relevant
* The notes start at the start token (<notes>) and end at the end token (</notes>)
* Github-style markdown syntax will be used to format the notes
    * Lists, which start with astericks (*) will be used dominantly to organize the notes
    * Indents will be used to nest lists
    * Headers, which start with hashes (#) will be used SPARINGLY to organize the notes
* The notes will be elaborate and detailed, but will not generate new section headers
* Each line will be kept short, simple and concise, and will not exceed 80 characters
* Multiple clauses or sentences will ALWAYS be broken into multiple lines 
* Only the next section of notes will be completed

\nAssistant:
<notes>
{notes}"""