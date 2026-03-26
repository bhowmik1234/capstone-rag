import axios from 'axios';

export interface PubMedArticle {
    id: string;
    title: string;
    abstract: string;
    date: string;
    url: string;
}

export class PubMedService {
    private eutilsBaseUrl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';

    async searchAndFetchArticles(query: string, maxResults: number = 3): Promise<PubMedArticle[]> {
        try {
            console.log(`Searching PubMed for: "${query}"`);
            
            // Search for IDs
            const searchResponse = await axios.get(`${this.eutilsBaseUrl}/esearch.fcgi`, {
                params: {
                    db: 'pubmed',
                    term: query,
                    retmode: 'json',
                    retmax: maxResults
                }
            });

            const ids: string[] = (searchResponse.data as any).esearchresult.idlist;
            
            if (!ids || ids.length === 0) {
                console.log('No PubMed articles found for query.');
                return [];
            }

            // Fetch summaries/abstracts
            // We use esummary for basic info. For abstracts, we might need efetch but esummary is easier to parse for JSON.
            // However, esummary doesn't always provide the full abstract in a clean way via JSON.
            // Let's use efetch with retmode=xml if needed, or esummary for title/date and a link.
            
            const articles: PubMedArticle[] = [];
            
            for (const id of ids) {
                const summaryResponse = await axios.get(`${this.eutilsBaseUrl}/esummary.fcgi`, {
                    params: {
                        db: 'pubmed',
                        id: id,
                        retmode: 'json'
                    }
                });

                const result = (summaryResponse.data as any).result[id];
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
        } catch (error: any) {
            console.error('Error fetching from PubMed:', error.message);
            return [];
        }
    }
}
