import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { setClusteredIris } from "../../actions/iris";
import axios from 'axios'

import { ProgressBar } from 'react-bootstrap';
import TrainingBoard from "./TrainingBoard";
import TrainedBoard from "./TrainedBoard";


export class IrisExplore extends Component {
  static propTypes = {
    iris: PropTypes.array.isRequired,
    getIris: PropTypes.func.isRequired,
  };

  constructor(props) {
    super(props);

    this.state = {
      cluster_number: 3,
      percentile: 0
    };
  }

  componentDidMount() {
  };

  queryTrainStatus(train_task_id){
     console.log("query train model..., with train task id=", train_task_id)

     axios.get(`/api/train?train_task_id=${train_task_id}`).then((resp)=>{
        console.log("data=", resp.data);

        let percentile = this.state.percentile;
        if( percentile <= 80 )
        {
          percentile += 10;
          this.setState({percentile: percentile});
        }

        let respData = JSON.parse(resp.data);
        let status = respData['status']
        if ("SUCCESS" === status) {
            let irisData = respData['result'];
            this.props.setClusteredIris(irisData);

            this.setState({percentile: 100});
        } else if ("FAILURE" === status) {
            console.log("train process failed!!");
        } else {
            setTimeout(() => {
                this.queryTrainStatus(train_task_id)
            }, 1000)
        }
     })
  }

  startTrain(){
    console.log("======start train =======")
    this.setState({percentile: 0});

    this.props.setClusteredIris([]);

    let cluster_number = this.state.cluster_number;

    axios.post("/api/train", {cluster_number: cluster_number}).then((resp)=>{
      console.log("data=", resp.data);

      let percentile = this.state.percentile;
      percentile += 10;
      this.setState({percentile: percentile})

      // this.queryTrainStatus(train_task_id)

      setTimeout(()=>{
        this.triggerOnlineTrain()
      }, 10000)  
    })
  }

  handleChange(e) {
    this.setState({cluster_number: e.target.value});
  }

  onSubmit = e => {
    e.preventDefault();
  }

  render() {
    let cluster_number = this.state.cluster_number;
    let percentile = this.state.percentile

    return (
      <Fragment>
        <form onSubmit={this.onSubmit.bind(this)}>
          <div className="form-group">
            <label>cluster number</label>
            <input
              className="form-control"
              type="text"
              name="cluster_number"
              onChange={this.handleChange.bind(this)}
              value={cluster_number}
            />
          </div>
          <ProgressBar animated now={percentile} label={`${percentile}%`}/>
          <br/>
          <div className="form-group">
            <button type="submit" className="btn btn-primary" onClick={this.startTrain.bind(this)}>start train</button>
          </div>
        </form>

        {
          this.state.percentile === 100 ? 
          <TrainedBoard clusterNumber={cluster_number}></TrainedBoard>
          : 
          <TrainingBoard setHook={hook => this.triggerOnlineTrain = hook} ></TrainingBoard>
        }
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
});

export default connect(
  mapStateToProps,
  { setClusteredIris }
)(IrisExplore);
