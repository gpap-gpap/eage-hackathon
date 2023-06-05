# Description

A code submission for a Hackathon at the 84rd EAGE Annual Conference, Vienna. The theme of this hackathon was "Natural Language Processing in the Geociences and Engineering".
A web tool which uses Natural Language Processing (NLP) to recommend abstracts from the submitted abstracts at the 84rd EAGE Annual Conference and on Google Scholar.

This can be done in three ways:

1. Search the most relevant abstracts based on selected abstracts. recommendation based on multiple abstracts is supported.
2. Find common terms in the suggested abstracts and automatically suggest past abstracts found on Google Scholar.
3. Search based on a search query to find the most relevant abstracts.

# Use

The tool can be accesed through the following link: https://gpap-gpap-eage-hackathon-public-jhptil.streamlit.app/.

The amount of recommended abstracts can be set to either 5, 10, or 20 by toggling the associated circular button found above. The top left widget can be used to toggle the abstracts
which are used to find relevant abstracts by clicking the "Generate recommedations" button. Relevant papers sorted on similiarity will be shown on the right. Moreover, you
can click the "...as well as these past EAGE classic papers!" button to find relevant papers on Google Scholar. Lastly, similiarity search based on a search query can be done below.

# Suggest future functionality

1. Use the search query search term found and the summaries of the recommended papers to make a ChatGPT promt to make an automatic literature review.
2. Improve the user interface and add the functionality to add multiple abstract databases.

# Developers:

Giorgos Papageorgiou - University of Edinburgh

Brian Eslick - Total Energies

Christiaan Oudshoorn - Idea League
