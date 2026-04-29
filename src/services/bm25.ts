export class BM25 {
    private documents: string[][] = [];
    private termFreqs: Map<string, number>[] = [];
    private docFreqs: Map<string, number> = new Map();
    private docLengths: number[] = [];
    private avgDocLength: number = 0;
    private k1: number;
    private b: number;

    constructor(k1: number = 1.5, b: number = 0.75) {
        this.k1 = k1;
        this.b = b;
    }

    private tokenize(text: string): string[] {
        return text.toLowerCase().match(/\w+/g) || [];
    }

    public fit(corpus: string[]) {
        let totalLen = 0;
        this.documents = corpus.map(doc => this.tokenize(doc));
        
        for (const doc of this.documents) {
            const tfs = new Map<string, number>();
            const uniqueTerms = new Set<string>();

            for (const term of doc) {
                tfs.set(term, (tfs.get(term) || 0) + 1);
                uniqueTerms.add(term);
            }

            this.termFreqs.push(tfs);
            this.docLengths.push(doc.length);
            totalLen += doc.length;

            for (const term of uniqueTerms) {
                this.docFreqs.set(term, (this.docFreqs.get(term) || 0) + 1);
            }
        }

        this.avgDocLength = corpus.length > 0 ? totalLen / corpus.length : 0;
    }

    public score(query: string): number[] {
        const queryTerms = this.tokenize(query);
        const scores: number[] = new Array(this.documents.length).fill(0);
        const N = this.documents.length;

        for (const term of queryTerms) {
            if (!this.docFreqs.has(term)) continue;

            const nq = this.docFreqs.get(term)!;
            const idf = Math.log(1 + (N - nq + 0.5) / (nq + 0.5));

            for (let i = 0; i < N; i++) {
                const tf = this.termFreqs[i].get(term) || 0;
                if (tf === 0) continue;

                const docLen = this.docLengths[i];
                const numerator = tf * (this.k1 + 1);
                const denominator = tf + this.k1 * (1 - this.b + this.b * (docLen / this.avgDocLength));
                
                scores[i] += idf * (numerator / denominator);
            }
        }

        return scores;
    }
}
