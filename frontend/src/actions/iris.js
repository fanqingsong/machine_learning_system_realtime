import axios from "axios";
import { createMessage, returnErrors } from "./messages";
import { tokenConfig } from "./auth";

import { SET_IRIS_DATA, DELETE_ONE_IRIS, UPDATE_ONE_IRIS, ADD_ONE_IRIS, SELECT_ONE_IRIS, SET_CLUSTERED_IRIS_DATA } from "./types";

// GET ALL IRIS DATA
export const getIris = () => (dispatch, getState) => {
  axios
    .get("/api/iris/", tokenConfig(getState))
    .then(res => {
      dispatch({
        type: SET_IRIS_DATA,
        payload: res.data
      });
    })
    .catch(err =>
      dispatch(returnErrors(err.response.data, err.response.status))
    );
};

// CLEAR ALL IRIS DATA
export const clearIris = () => (dispatch, getState) => {
    dispatch({
      type: SET_IRIS_DATA,
      payload: undefined
    });
};

// DELETE one iris
export const deleteOneIris = id => (dispatch, getState) => {
  axios
    .delete(`/api/iris/${id}/`, tokenConfig(getState))
    .then(res => {
      dispatch(createMessage({ deleteOneIris: "iris Deleted" }));
      dispatch({
        type: DELETE_ONE_IRIS,
        payload: id
      });
    })
    .catch(err => console.log(err));
};

// select one iris to be edited.
export const selectOneIrisToUpdate = iris => (dispatch, getState) => {
  console.log("selectOneIrisToUpdate called");
  dispatch({
    type: SELECT_ONE_IRIS,
    payload: iris
  })
}

// UPDATE one iris
export const updateOneIris = iris => (dispatch, getState) => {
  axios
    .put(`/api/iris/${iris.id}/`, iris, tokenConfig(getState))
    .then(res => {
      dispatch(createMessage({ updateOneIris: "iris Updated" }));
      dispatch({
        type: UPDATE_ONE_IRIS,
        payload: iris
      });
    })
    .catch(err => console.log(err));
};

// ADD one iris
export const addOneIris = iris => (dispatch, getState) => {
  axios
    .post("/api/iris/", iris, tokenConfig(getState))
    .then(res => {
      console.log("add one iris success", res.data);

      dispatch(createMessage({ addOneIris: "iris Added" }));
      
      dispatch({
        type: ADD_ONE_IRIS,
        payload: res.data
      });
    })
    .catch(err =>
      dispatch(returnErrors(err.response.data, err.response.status))
    );
};

// store data from trained model
export const setClusteredIris = clusteredIris => (dispatch, getState) => {
  console.log("setClusteredIris called");
  dispatch({
    type: SET_CLUSTERED_IRIS_DATA,
    payload: clusteredIris
  })
}

