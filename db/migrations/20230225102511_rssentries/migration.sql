-- CreateTable
CREATE TABLE "RssEntries" (
    "id" INTEGER NOT NULL,
    "feed" TEXT NOT NULL,

    CONSTRAINT "RssEntries_pkey" PRIMARY KEY ("id","feed")
);

-- AddForeignKey
ALTER TABLE "RssEntries" ADD CONSTRAINT "RssEntries_id_fkey" FOREIGN KEY ("id") REFERENCES "NewsSources"("id") ON DELETE CASCADE ON UPDATE CASCADE;
