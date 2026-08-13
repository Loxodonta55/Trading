export const LEVERAGED_ETFS = {
  TSLA: {
    name: 'Tesla Inc.',
    underlying: 'TSLA',
    primaryLeverageText: 'TSLL (2x Bull)',
    longUS: {
      ticker: 'TSLL',
      name: 'Direxion Daily TSLA Bull 2X Shares',
      leverage: '2x Long',
      isin: 'US25461A4099',
      exchange: 'NASDAQ (IBKR US)'
    },
    longEU: {
      ticker: '3LTS',
      name: 'GraniteShares 3x Long Tesla Daily ETP',
      leverage: '3x Long',
      isin: 'XS2822013898',
      exchange: 'LSE / XETRA (IBKR Europe)'
    },
    shortUS: {
      ticker: 'TSLS',
      name: 'Direxion Daily TSLA Bear 1X Shares',
      leverage: '1x Bear / Short',
      isin: 'US25461A3000',
      exchange: 'NASDAQ (IBKR US)'
    },
    shortEU: {
      ticker: '3STS',
      name: 'GraniteShares 3x Short Tesla Daily ETP',
      leverage: '3x Short',
      isin: 'XS2822013971',
      exchange: 'LSE / XETRA (IBKR Europe)'
    }
  },
  GOOGL: {
    name: 'Alphabet Inc.',
    underlying: 'GOOGL',
    primaryLeverageText: 'GGLL (2x Bull)',
    longUS: {
      ticker: 'GGLL',
      name: 'Direxion Daily GOOGL Bull 2X Shares',
      leverage: '2x Long',
      isin: 'US25461A4255',
      exchange: 'NASDAQ (IBKR US)'
    },
    longEU: {
      ticker: '3LGO',
      name: 'GraniteShares 3x Long Alphabet Daily ETP',
      leverage: '3x Long',
      isin: 'XS2822014011',
      exchange: 'LSE / XETRA (IBKR Europe)'
    },
    shortUS: {
      ticker: 'GGLS',
      name: 'Direxion Daily GOOGL Bear 1X Shares',
      leverage: '1x Bear / Short',
      isin: 'US25461A4339',
      exchange: 'NASDAQ (IBKR US)'
    },
    shortEU: {
      ticker: '3SGO',
      name: 'GraniteShares 3x Short Alphabet Daily ETP',
      leverage: '3x Short',
      isin: 'XS2822014193',
      exchange: 'LSE / XETRA (IBKR Europe)'
    }
  },
  SPCX: {
    name: 'SpaceX Track & S&P 500',
    underlying: 'SPCX / SPY',
    primaryLeverageText: 'UPRO (3x Bull)',
    longUS: {
      ticker: 'UPRO',
      name: 'ProShares UltraPro S&P500 3X',
      leverage: '3x Long',
      isin: 'US74347X8569',
      exchange: 'NYSE Arca (IBKR US)'
    },
    longEU: {
      ticker: '3USL',
      name: 'GraniteShares 3x Long US 500 Daily ETP',
      leverage: '3x Long',
      isin: 'XS2788730998',
      exchange: 'LSE / XETRA (IBKR Europe)'
    },
    shortUS: {
      ticker: 'SPXU',
      name: 'ProShares UltraPro Short S&P500 -3X',
      leverage: '3x Short',
      isin: 'US74347X8494',
      exchange: 'NYSE Arca (IBKR US)'
    },
    shortEU: {
      ticker: '3USS',
      name: 'GraniteShares 3x Short US 500 Daily ETP',
      leverage: '3x Short',
      isin: 'XS2788731020',
      exchange: 'LSE / XETRA (IBKR Europe)'
    },
    specialTrack: {
      ticker: 'DXYZ',
      name: 'Destiny Tech100 (SpaceX Direct Portfolio Holding auf IBKR)',
      leverage: 'Private Equity Track',
      isin: 'US25064A1034',
      exchange: 'NYSE (IBKR)'
    }
  },
  NVDA: {
    name: 'NVIDIA Corp.',
    underlying: 'NVDA',
    primaryLeverageText: 'NVDL (2x Bull)',
    longUS: {
      ticker: 'NVDL',
      name: 'GraniteShares 2x Long NVDA Daily ETF',
      leverage: '2x Long',
      isin: 'US38747R6057',
      exchange: 'NASDAQ (IBKR US)'
    },
    longEU: {
      ticker: '3LNV',
      name: 'GraniteShares 3x Long NVIDIA Daily ETP',
      leverage: '3x Long',
      isin: 'XS2822013468',
      exchange: 'LSE / XETRA (IBKR Europe)'
    },
    shortUS: {
      ticker: 'NVDD',
      name: 'GraniteShares 2x Short NVDA Daily ETF',
      leverage: '2x Short',
      isin: 'US38747R5067',
      exchange: 'NASDAQ (IBKR US)'
    },
    shortEU: {
      ticker: '3SNV',
      name: 'GraniteShares 3x Short NVIDIA Daily ETP',
      leverage: '3x Short',
      isin: 'XS2822013542',
      exchange: 'LSE / XETRA (IBKR Europe)'
    }
  }
};
