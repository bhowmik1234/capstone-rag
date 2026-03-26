import axios from 'axios';
export class PubMedService {
    eutilsBaseUrl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';
    async searchAndFetchArticles(query, maxResults = 3) {
        try {
            console.log(`Searching PubMed for: "${query}"`);
            // 1. Search for IDs
            const searchResponse = await axios.get(`${this.eutilsBaseUrl}/esearch.fcgi`, {
                params: {
                    db: 'pubmed',
                    term: query,
                    retmode: 'json',
                    retmax: maxResults
                }
            });
            const ids = searchResponse.data.esearchresult.idlist;
            if (!ids || ids.length === 0) {
                console.log('No PubMed articles found for query.');
                return [];
            }
            // 2. Fetch summaries/abstracts
            // We use esummary for basic info. For abstracts, we might need efetch but esummary is easier to parse for JSON.
            // However, esummary doesn't always provide the full abstract in a clean way via JSON.
            // Let's use efetch with retmode=xml if needed, or esummary for title/date and a link.
            const articles = [];
            for (const id of ids) {
                const summaryResponse = await axios.get(`${this.eutilsBaseUrl}/esummary.fcgi`, {
                    params: {
                        db: 'pubmed',
                        id: id,
                        retmode: 'json'
                    }
                });
                const result = summaryResponse.data.result[id];
                if (result) {
                    articles.push({
                        id: id,
                        title: result.title,
                        abstract: result.description || 'No abstract available.', // description often contains a snippet or summary
                        date: result.pubdate,
                        url: `https://pubmed.ncbi.nlm.nih.gov/${id}/`
                    });
                }
            }
            return articles;
        }
        catch (error) {
            console.error('Error fetching from PubMed:', error.message);
            return [];
        }
    }
}
