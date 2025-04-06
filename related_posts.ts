import { getAllPosts, getCondensedPost, getFileNameFromSlug } from "./mdx";
import { Corpus, Similarity } from 'tiny-tfidf';

const fs = require('fs');

const relatedPostsFile = './public/relatedMatrix.json';

export type FrontMatter = {
  title: string;
  layout: string;
  date?: Date | string,
  hn?: string;
  unpublished?: boolean;
  image?: string;
  description?: string;
  tags: string[];
  categories: string[];
  readingTime?: {
    minutes: number,
    words: number
  }
};

export type RelatedPosts = {
  slugs: string[],
  categories?: string[],
  frontmatters: (FrontMatter | null)[],
};

export type RelatedPostMatrices = {
  [index: string]: RelatedPosts
}

type DistanceMatrix = {
  identifiers: string[],
  matrix: number[][],
  strongestCategories?: number[][],
}

type StrengthVector = {
  identifiers: string[],
  vector: number[]
}

type RelatedPostMetric = {
  id: string;
  description: string;
  threshold: number;
  multiplier: number;
}

function applyMatrixThreshold(distanceMatrixVector: DistanceMatrix | StrengthVector, threshold: number): DistanceMatrix | StrengthVector {
  if('matrix' in distanceMatrixVector)
    return {
      identifiers: distanceMatrixVector.identifiers,
      matrix: distanceMatrixVector.matrix.map(col => col.map(row => !isNaN(row) && row <= threshold ? row : 1))
    }
  else
    return {
      identifiers:  distanceMatrixVector.identifiers,
      vector: distanceMatrixVector.vector.map(v => !isNaN(v) && v <= threshold ? v : 1 )
    }
}

function normalizeVector(vector: number[]) {
  const normalizeVal = (val: number, max: number, min: number): number => {
    return(val - min) / (max - min);
  }

  const max = Math.max.apply(null, vector);
  const min = Math.min.apply(null, vector);

  const normalizedVector = vector.map(val => normalizeVal(val, max, min));

  return normalizedVector;
}

function applyFunc(incoming: DistanceMatrix | StrengthVector, func: (inp: number) => number) {
  if('matrix' in incoming) {
    return {
      ...incoming,
      matrix: incoming.matrix.map(r => r.map(c => func(c)))
    }
  } else {
    return {
      ...incoming,
      vector: incoming.vector.map(r => func(r))
    }
  }
}

function customSigmoid(inp: number): number {
  return 1./(1.+Math.exp(-8.*(inp-0.5)))
}

function invertNormalized(inp: number): number {
  return 1-inp;
}

function convoluteAddWithMultiplier(baseMatrix: DistanceMatrix, incoming: DistanceMatrix | StrengthVector, multiplier: number): DistanceMatrix {
  if('vector' in incoming) {
    incoming.vector = incoming.vector.map(val => val*multiplier);
    baseMatrix.matrix = baseMatrix.matrix.map((r, rowIndex) => r.map((c, colIndex) => incoming.vector[colIndex]+c));
  } else {
    incoming.matrix = incoming.matrix.map(row => row.map(val => val*multiplier));
    baseMatrix.matrix = baseMatrix.matrix.map((r, rowIndex) => r.map((c, colIndex) => incoming.matrix[rowIndex][colIndex]+c));
  }

  return baseMatrix;
}

export function checkBuildRelatedPosts() {
  if(!fs.existsSync(relatedPostsFile))
    generateRelatedPosts();
}

export const generateRelatedPosts = () => {
  console.log("Building related posts");
  const posts = getAllPosts(true);

  console.time("Generating corpus");

  const postTitleCorpus = new Corpus(posts.map(post => post.slug), posts.map(post => post.frontmatter.title + post.frontmatter.description));

  const postTagCategoryCorpus = new Corpus(posts.map(post => post.slug),
    posts.map(post =>
      (((post.frontmatter.categories && post.frontmatter.categories.join(" ")) || "")+
      ((post.frontmatter.tags && post.frontmatter.tags.join(" ")) || "")) || (post.frontmatter.title + post.frontmatter.description)
    )
  );

  const postContentCorpus = new Corpus(posts.map(post => post.slug), posts.map(post => post.markdown));

  console.timeEnd("Generating corpus");

  console.time("Computing metric data");

  const metricData: {
    [index: string]: DistanceMatrix | StrengthVector
  } = {};

  for(let i=0;i<metrics.length;i++) {
    switch(metrics[i].id) {
      case 'titles':
        metricData[metrics[i].id] = new Similarity(postTitleCorpus).getDistanceMatrix() as DistanceMatrix;
        break;
      case 'content':
        metricData[metrics[i].id] = new Similarity(postContentCorpus).getDistanceMatrix() as DistanceMatrix;
        break;
      case 'tagCats':
        metricData[metrics[i].id] = new Similarity(postTagCategoryCorpus).getDistanceMatrix() as DistanceMatrix;
        break;
      case 'recency':
        metricData[metrics[i].id] = applyFunc(
          {
            identifiers: posts.map(post => post.slug),
            vector:
                normalizeVector(
                  posts.map(post => post.frontmatter.date ? (new Date().getTime()-new Date(post.frontmatter.date).getTime()) : 0),
                )
          }, customSigmoid);
        break;
      default:
        throw new Error("Metric detected without any data generation code.");
    }

    // Fix this when you land
    metricData[metrics[i].id] = applyMatrixThreshold(metricData[metrics[i].id], metrics[i].threshold);

    metricData[metrics[i].id] = applyFunc(metricData[metrics[i].id], invertNormalized);
  }

  console.timeEnd("Computing metric data");

  console.time("Convoluting...");

  let finalMatrix: DistanceMatrix = {
    identifiers: JSON.parse(JSON.stringify(metricData.titles.identifiers)),
    matrix: (metricData.titles as DistanceMatrix).matrix.map(r => r.map(c => 0)),
  }

  let strongestCategories = (metricData.titles as DistanceMatrix).matrix.map(r => r.map(c => null as null | {category: number, val: number}));

  for(let i=0;i<metrics.length;i++) {
    const metric = metrics[i];

    let incoming = metricData[metric.id];
    finalMatrix = convoluteAddWithMultiplier(finalMatrix, incoming, metric.multiplier);

    if('matrix' in incoming) {
      incoming.matrix.map((r, rIndex) => r.map((c, cIndex) => {
        const newVal = c * metric.multiplier;
        const existingVal = strongestCategories[rIndex][cIndex];
        if(!existingVal || existingVal.val < newVal)
          strongestCategories[rIndex][cIndex] = {
            category: i,
            val: newVal
          }
      }));
    } else {
      incoming.vector.map((r, rIndex) => {
        const newVal = r * metric.multiplier;
        strongestCategories.map((sc, scIndex) => {
          const existingVal = strongestCategories[rIndex][scIndex];
          if(!existingVal || existingVal.val < newVal)
            strongestCategories[rIndex][scIndex] = {
              category: i,
              val: newVal
            }
        });
      });
    }
  }

  finalMatrix.strongestCategories = strongestCategories.map(r => r.map(c => c && c.category || 0));

  console.timeEnd("Convoluting...");

  console.time("Writing to file...");
  fs.writeFileSync(relatedPostsFile, JSON.stringify({...metricData, final: finalMatrix}));
  console.timeEnd("Writing to file...");
}


export function getRelatedPosts(slug: string): RelatedPostMatrices {
  checkBuildRelatedPosts();
  const matrices: {
    [index: string]: DistanceMatrix | StrengthVector
  } = JSON.parse(fs.readFileSync(relatedPostsFile));

  let slugIndex = matrices.final.identifiers.findIndex(val => val === slug);

  if(slugIndex === -1)
    slugIndex = 0;

  let relatedPosts: RelatedPostMatrices = {};

  Object.keys(matrices).map(type => {
    if('matrix' in matrices[type]) {
      const scores = (matrices[type] as DistanceMatrix).matrix[slugIndex]
                  .map((score, index) => ({score, index}))
                  .sort((a,b) => {
                    return b.score-a.score
                  })
                  .filter(score => score.score > 0 && score.index !== slugIndex);

      relatedPosts[type] = {
        slugs: scores.map(score => matrices[type].identifiers[score.index]),
        frontmatters: scores.map(score => {
          try {
            return getCondensedPost(getFileNameFromSlug(matrices[type].identifiers[score.index])).frontmatter
          } catch(err) {
            console.error("Error reading frontmatter for slug ",getFileNameFromSlug(matrices[type].identifiers[score.index])," - ",err);
            return null;
          }
        })
      }

      if((matrices[type] as DistanceMatrix).strongestCategories) {
        relatedPosts[type].categories = scores
          .map(score => (matrices[type] as DistanceMatrix).strongestCategories![slugIndex][score.index])
          .map(catIndex => metrics[catIndex].description)
      }
    } else {
      const scores = (matrices[type] as StrengthVector).vector
        .map((score, index) => ({score, index}))
        .sort((a,b) => b.score-a.score);

      relatedPosts[type] = {
        slugs: scores.map(c => matrices[type].identifiers[c.index]),
        frontmatters: scores.map(score => {
          try {
            return getCondensedPost(getFileNameFromSlug(matrices[type].identifiers[score.index])).frontmatter
          } catch(err) {
            console.error("Error reading frontmatter for slug ",getFileNameFromSlug(matrices[type].identifiers[score.index])," - ",err);
            return null;
          }
        })
      }
    }

  })

  return relatedPosts;
}



const metrics: RelatedPostMetric[] = [
  {
    id: 'titles',
    description: 'Similar',
    multiplier: 8,
    threshold: 1
  },
  {
    id: 'tagCats',
    description: 'Same Category',
    multiplier: 10,
    threshold: 1,
  },
  {
    id: 'content',
    description: 'Similar',
    multiplier: 8,
    threshold: 0.91
  },
  {
    id: 'recency',
    description: 'New',
    multiplier: 1,
    threshold: 0.3
  }
]