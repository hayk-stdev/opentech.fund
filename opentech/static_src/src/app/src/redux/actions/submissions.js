import api from '@api';


export const SET_CURRENT_SUBMISSION_ROUND = 'SET_CURRENT_SUBMISSION_ROUND';

export const UPDATE_SUBMISSIONS_BY_ROUND = 'UPDATE_SUBMISSIONS_BY_ROUND';

export const setCurrentSubmissionRound = id => ({
    type: SET_CURRENT_SUBMISSION_ROUND,
    id,
});

export const fetchSubmissionsByRound = id => {
    return async function(dispatch) {
        //dispatch(fetchSubmissionsByRoundBegin());
        try {
            const response = await api.fetchSubmissionsByRound(id);
            const json = await response.json();
            if (!response.ok) {
                // handle error
            }
            dispatch(updateSubmissionsByRound(id, json));
        } catch (e) {
            console.error(e);
            // handle error
        }
    };
};


export const updateSubmissionsByRound = (roundId, data) => ({
    type: UPDATE_SUBMISSIONS_BY_ROUND,
    roundId,
    data,
});