-- CreateTable
CREATE TABLE "NewsArticles" (
    "id" SERIAL NOT NULL,
    "source_id" INTEGER NOT NULL,
    "url" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "photo" BYTEA NOT NULL,
    "publication_date" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "NewsArticles_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "NewsArticles" ADD CONSTRAINT "NewsArticles_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "NewsSources"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
