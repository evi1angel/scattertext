import pandas as pd
import numpy as np
from scipy.stats import norm
from scattertext.termscoring.CorpusBasedTermScorer import CorpusBasedTermScorer, sparse_var


class CohensD(CorpusBasedTermScorer):
    '''
    Cohen's d scores

    term_scorer = (CohensD(corpus).set_categories('Positive', ['Negative'], ['Plot']))

    html = st.produce_frequency_explorer(
        corpus,
        category='Positive',
        not_categories=['Negative'],
        neutral_categories=['Plot'],
        term_scorer=term_scorer,
        metadata=rdf['movie_name'],
        grey_threshold=0,
        show_neutral=True
    )
    file_name = 'rotten_fresh_fre.html'
    open(file_name, 'wb').write(html.encode('utf-8'))
    IFrame(src=file_name, width=1300, height=700)
    '''

    def _set_scorer_args(self, **kwargs):
        pass

    def get_scores(self, *args):
        return self.get_score_df()['cohens_d']

    def get_score_df(self):
        # From https://people.kth.se/~lang/Effect_size.pdf
        # Shinichi Nakagawa1 and Innes C. Cuthill. 2007. In Biological Reviews 82.
        X = self._get_X().astype(np.float64)
        X = X / X.sum(axis=1)
        cat_X, ncat_X = self._get_cat_and_ncat(X)
        n1, n2 = float(cat_X.shape[1]), float(ncat_X.shape[1])
        n = n1 + n2
        m1 = cat_X.mean(axis=0).A1
        m2 = ncat_X.mean(axis=0).A1
        v1 = cat_X.var(axis=0).A1
        v2 = ncat_X.var(axis=0).A1
        s_pooled = np.sqrt(((n2 - 1) * v2 + (n1 - 1) * v1) / (n - 2.))
        cohens_d = (m1 - m2) / s_pooled
        cohens_d_se = np.sqrt(((n - 1.) / (n - 3)) * (4. / n) * (1 + np.square(cohens_d)))
        cohens_d_z = cohens_d / cohens_d_se
        cohens_d_p = norm.sf(cohens_d_z)
        hedges_r = cohens_d * (1 - 3. / ((4. * (n - 2)) - 1))
        hedges_r_se = np.sqrt(n / (n1 * n2) + np.square(hedges_r) / (n - 2.))
        hedges_r_z = hedges_r / hedges_r_se
        hedges_r_p = norm.sf(hedges_r_z)

        score_df = pd.DataFrame({
            'cohens_d': cohens_d,
            'cohens_d_se': cohens_d_se,
            'cohens_d_z': cohens_d_z,
            'cohens_d_p': cohens_d_p,
            'hedges_r': hedges_r,
            'hedges_r_se': hedges_r_se,
            'hedges_r_z': hedges_r_z,
            'hedges_r_p': hedges_r_p,
            'm1': m1,
            'm2': m2
        }, index=self.corpus_.get_terms()).fillna(0)
        return score_df

    def get_name(self):
        return "Cohen's d"


class HedgesR(CohensD):
    def get_scores(self, *args):
        return self.get_score_df()['hedges_r']

    def get_name(self):
        return "Hedge's r"
