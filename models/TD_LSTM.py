from layers.Dynamic_RNN import DynamicRNN
import torch
import torch.nn as nn


class TD_LSTM(nn.Module):
    def __init__(self, args, embedding_matrix=None, aspect_embedding_matrix=None):
        super(TD_LSTM, self).__init__()
        self.args = args
        self.encoder = nn.Embedding.from_pretrained(torch.tensor(embedding_matrix, dtype=torch.float))
        self.encoder_aspect = nn.Embedding.from_pretrained(torch.tensor(aspect_embedding_matrix, dtype=torch.float))
        self.lstm_l = DynamicRNN(args.embed_dim, args.hidden_dim, num_layers=1, batch_first=True, dropout=args.dropout,
                                 rnn_type="LSTM")
        self.lstm_r = DynamicRNN(args.embed_dim, args.hidden_dim, num_layers=1, batch_first=True, dropout=args.dropout,
                                 rnn_type="LSTM")
        self.dense = nn.Linear(args.hidden_dim * 2, args.polarities_dim)
        self.dropout = nn.Dropout(args.dropout)
        self.softmax = nn.Softmax()

    def forward(self, inputs):
        x_l, x_r = inputs[0], inputs[1]
        x_l_len, x_r_len = torch.sum(x_l != 0, dim=-1), torch.sum(x_r != 0, dim=-1)
        x_l, x_r = self.encoder(x_l), self.encoder(x_r)
        x_l, x_r = self.dropout(x_l), self.dropout(x_r)
        _, (h_n_l, _) = self.lstm_l(x_l, x_l_len)
        _, (h_n_r, _) = self.lstm_r(x_r, x_r_len)
        h_n = torch.cat((h_n_l[0], h_n_r[0]), dim=-1)
        output = self.dropout(h_n)
        output = self.dense(output)
        if self.args.softmax:
            output = self.softmax(output)
        return output
