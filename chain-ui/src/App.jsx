import React, { useState, useEffect } from "react";
import { Container, Typography, Button, TextField, Card, CardContent, Snackbar, AppBar, Toolbar, Grid, IconButton } from "@mui/material";
import MuiAlert from "@mui/material/Alert";
import { Send, AccountBalanceWallet, History, Gavel, Storage } from "@mui/icons-material";
import axios from "axios";

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default function CryptoDashboard() {
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [blockchain, setBlockchain] = useState([]);
  
  useEffect(() => {
    fetchBalance();
    fetchTransactions();
  }, []);

  const fetchBalance = async () => {
    const res = await axios.get("http://localhost:5001/calculate_balance");
    setBalance(res.data.balance);
  };

  const fetchTransactions = async () => {
    const res = await axios.get("http://localhost:5001/show_transactions");
    if (res.data.pending_transactions) {
      try {
        const transactionsArray = res.data.pending_transactions;
        setTransactions(transactionsArray);
      } catch (error) {
        setTransactions([]);
      }
    } else {
      setTransactions([]);
    }
  };

  const handleTransaction = async () => {
    try {
      const res = await axios.post("http://localhost:5001/add_transaction", {
        receiver,
        amount: parseFloat(amount),
      });
      setMessage(res.data.message);
      setOpen(true);
      fetchBalance();
      fetchTransactions();
    } catch (error) {
      setMessage("Transaction failed!");
      setOpen(true);
    }
  };

  const mineBlock = async () => {
    try {
      const res = await axios.get("http://localhost:5001/mine_block");
      setMessage(res.data.message);
      setOpen(true);
      fetchBalance();
      fetchTransactions();
    } catch (error) {
      setMessage("Mining failed!");
      setOpen(true);
    }
  };

  const fetchBlockchain = async () => {
    try {
      const res = await axios.get("http://localhost:5001/get_chain");
      setBlockchain(res.data.chain);
      setMessage("Blockchain fetched successfully!");
      setOpen(true);
    } catch (error) {
      setMessage("Failed to fetch blockchain!");
      setOpen(true);
    }
  };

  return (
    <Container maxWidth={false} sx={{ minHeight: "100vh", px: 3 }}>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Crypto Dashboard</Typography>
        </Toolbar>
      </AppBar>
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 3, textAlign: "center" }}>
            <AccountBalanceWallet sx={{ fontSize: 40, color: "#1976d2" }} />
            <Typography variant="h5" sx={{ mt: 2 }}>Balance</Typography>
            <Typography variant="h4" sx={{ fontWeight: "bold", mt: 1 }}>{balance} Coins</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6">Make a Transaction</Typography>
            <TextField
              label="Receiver Address"
              variant="outlined"
              fullWidth
              margin="normal"
              value={receiver}
              onChange={(e) => setReceiver(e.target.value)}
            />
            <TextField
              label="Amount"
              type="number"
              variant="outlined"
              fullWidth
              margin="normal"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <Button 
              variant="contained" 
              color="primary" 
              fullWidth 
              startIcon={<Send />} 
              sx={{ mt: 2 }}
              onClick={handleTransaction}
            >
              Send Coins
            </Button>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              <History sx={{ mr: 1 }} /> Pending Transactions
            </Typography>
            {transactions.length > 0 ? (
              transactions.map((tx, index) => (
                <Card key={index} sx={{ mb: 2, p: 2 }}>
                  <Typography>
                    {tx.sender.slice(0, 6)}... ➝ {tx.receiver.slice(0, 6)}... : {tx.amount} Coins
                  </Typography>
                </Card>
              ))
            ) : (
              <Typography>No pending transactions</Typography>
            )}
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Button 
            variant="contained" 
            color="secondary" 
            fullWidth 
            startIcon={<Gavel />} 
            sx={{ mt: 2 }}
            onClick={mineBlock}
          >
            Mine Block
          </Button>
        </Grid>
        <Grid item xs={12}>
          <Button 
            variant="contained" 
            color="info" 
            fullWidth 
            startIcon={<Storage />} 
            sx={{ mt: 2 }}
            onClick={fetchBlockchain}
          >
            View Blockchain
          </Button>
        </Grid>
        {blockchain.length > 0 && (
          <Grid item xs={12}>
            <Card sx={{ p: 3 }}>
              <Typography variant="h6">Blockchain</Typography>
              {blockchain.map((block, index) => (
                <Card key={index} sx={{ my: 2, p: 2 }}>
                  <Typography>Index: {block.index}</Typography>
                  <Typography>Timestamp: {block.timestamp}</Typography>
                  <Typography>Previous Hash: {block.previous_hash}</Typography>
                  <Typography>Transactions: {JSON.stringify(block.transactions)}</Typography>
                </Card>
              ))}
            </Card>
          </Grid>
        )}
      </Grid>
      <Snackbar open={open} autoHideDuration={6000} onClose={() => setOpen(false)}>
        <Alert onClose={() => setOpen(false)} severity="success">{message}</Alert>
      </Snackbar>
    </Container>
  );
}
