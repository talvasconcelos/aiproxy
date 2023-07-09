const mapLinks = obj => {
  obj._data = _.clone(obj)
  return obj
}

new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: function () {
    return {
      links: [],
      formDialog: {
        show: false,
        data: {}
      },
      links: [],
      linksTable: [
        {name: 'id', align: 'left', label: 'ID', field: 'id'},
        {name: 'api_url', align: 'left', label: 'URL', field: 'api_url'},
        {name: 'api_key', align: 'left', label: 'Key', field: 'api_url'},
        {name: 'wallet', align: 'left', label: 'Wallet', field: 'wallet'},
        {name: 'cost', align: 'left', label: 'Cost', field: 'cost'}
      ],
      pagination: {
        rowsPerPage: 10
      }
    }
  },

  methods: {
    getLinks() {
      LNbits.api
        .request(
          'GET',
          '/aiproxy/api/v1/links?all_wallets=true',
          this.g.user.wallets[0].inkey
        )
        .then(response => {
          this.links = response.data
          console.log(this.links)
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    resetFormDialog() {
      this.formDialog.show = false
      this.formDialog.data = {}
    },
    openUpdateForm(id) {
      const link = this.links.find(l => l.id === id)
      this.formDialog.data = {...link}
      this.formDialog.show = true
    },
    deleteLink(id) {
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this link?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              `/aiproxy/api/v1/links/${id}`,
              this.g.user.wallets[0].adminkey
            )
            .then(() => {
              this.links = this.links.filter(l => l.id !== id)
              this.$q.notify({
                message: `Link deleted.`,
                timeout: 700
              })
            })
            .catch(error => {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    sendForm() {
      const wallet = this.g.user.wallets.find(
        w => w.id === this.formDialog.data.wallet
      )
      const data = {...this.formDialog.data}
      if (!data.cost) data.cost = 0
      if (data.id) {
        this.updateLink(wallet, data)
      } else {
        this.createLink(wallet, data)
      }
    },
    createLink(wallet, data) {
      LNbits.api
        .request('POST', '/aiproxy/api/v1/links', wallet.inkey, data)
        .then(response => {
          this.links.push(response.data)
          this.$q.notify({
            type: 'positive',
            message: `Link created.`,
            timeout: 700
          })
          this.resetFormDialog()
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    },
    updateLink(wallet, data) {
      LNbits.api
        .request('PUT', `/aiproxy/api/v1/links/${data.id}`, wallet.inkey, data)
        .then(response => {
          const index = this.links.findIndex(l => l.id === data.id)
          this.links.splice(index, 1, response.data)
          this.$q.notify({
            type: 'positive',
            message: `Link updated.`,
            timeout: 700
          })
          this.resetFormDialog()
        })
        .catch(error => {
          LNbits.utils.notifyApiError(error)
        })
    }
  },

  created() {
    this.getLinks()
  }
})
