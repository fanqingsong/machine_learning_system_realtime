import { SET_IRIS_DATA, DELETE_ONE_IRIS, SELECT_ONE_IRIS, UPDATE_ONE_IRIS, ADD_ONE_IRIS, CLEAR_IRIS_DATA, SET_CLUSTERED_IRIS_DATA } from "../actions/types.js";

const initialState = {
  // data from db
  iris: [],
  // for update
  oneSelectedIris: {
    sepal_len: "",
    sepal_width: "",
    petal_len: "",
    petal_width: "",
    category: ""
  },
  // data from trained model
  clusteredIris: []
};

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_IRIS_DATA:
      return {
        ...state,
        iris: action.payload
      };
    case CLEAR_IRIS_DATA:
      return {
        ...state,
        iris: []
      };  
    case ADD_ONE_IRIS:
      return {
        ...state,
        iris: [...state.iris, action.payload]
      };  
    case DELETE_ONE_IRIS:
      return {
        ...state,
        iris: state.iris.filter(one_iris => one_iris.id !== action.payload)
      };
    case UPDATE_ONE_IRIS:
      return {
        ...state,
        iris: state.iris.map(one_iris => {
                  if ( one_iris.id !== action.payload.id ) {
                    return one_iris;
                  } else {
                    return action.payload;
                  }
                })
      };  
    case SELECT_ONE_IRIS:
      console.log("in reducer SELECT_ONE_IRIS is called");
      return {
        ...state,
        oneSelectedIris: action.payload
      };
    case SET_CLUSTERED_IRIS_DATA:
      console.log("in reducer SET_CLUSTERED_IRIS_DATA is called");
      console.log(action.payload)
      return {
        ...state,
        clusteredIris: action.payload
      };
    default:
      return state;
  }
}
