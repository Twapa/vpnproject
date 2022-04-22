var app = new Vue({
    el: '#app',
    data: {
      message: 'H try!',
      svdata: {}
    },
    created: function() {
      this.loadData();
    },
    methods: {
        loadData: async function() {
            console.log("Loading data");
            const response = await fetch('/data_api', {cache: "no-store"});
            const data = await response.json();
            this.svdata = data;
            setTimeout(this.loadData, 15000);
        }
        
    }
  })